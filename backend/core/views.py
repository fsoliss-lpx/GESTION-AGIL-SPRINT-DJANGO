import json
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.db import transaction 
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Tarea, Proyecto, MiembroProyecto, Usuario, Sprint, Evidencia, Notificacion
from .forms import RegistroUsuarioForm


def registro(request):
    """Vista para que nuevos usuarios creen su cuenta y vayan al login formal."""
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()  # Guardamos el usuario en la base de datos de forma segura
            
            # Mensaje flash opcional para avisarle al estudiante que ya puede ingresar
            messages.success(request, "Cuenta institucional creada con éxito. Por favor, inicia sesión.")
            
            # Cambiamos la redirección para que vaya al Login en lugar del Dashboard
            return redirect('login')  # O como tengas nombrada la ruta de login en tu urls.py (ej: 'core:login')
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'registro.html', {'form': form})


@login_required
def dashboard(request):
    """Vista principal del panel de control con separación de proyectos."""
    proyectos_base = Proyecto.objects.filter(
        models.Q(creador=request.user) | models.Q(miembros__usuario=request.user),
        is_active=True
    ).distinct()

    proyectos_vigentes = proyectos_base.filter(es_finalizado=False)
    proyectos_finalizados = proyectos_base.filter(es_finalizado=True)

    menciones = Notificacion.objects.filter(
        usuario_mencionado=request.user,
        leido=False
    ).select_related('autor_mencion', 'tarea__sprint__proyecto')

    context = {
        'proyectos': proyectos_vigentes,
        'proyectos_finalizados': proyectos_finalizados,
        'menciones': menciones,
        'menciones_count': menciones.count(),
    }
    return render(request, 'dashboard.html', context)


@login_required
def crear_proyecto(request):
    """Vista para registrar un nuevo proyecto incluyendo fechas de inicio y fin."""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        fecha_inicio = request.POST.get('fecha_inicio') or None
        fecha_fin = request.POST.get('fecha_fin') or None
        
        if nombre:
            nuevo_proyecto = Proyecto.objects.create(
                nombre=nombre, 
                descripcion=descripcion, 
                creador=request.user,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            MiembroProyecto.objects.create(
                proyecto=nuevo_proyecto,
                usuario=request.user,
                rol='PO'
            )
            return redirect('core:dashboard')
            
    return redirect('core:dashboard')


@login_required
def detalle_proyecto(request, proyecto_id):
    """Vista para gestionar el equipo del proyecto con bloque transaccional."""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if not MiembroProyecto.objects.filter(proyecto=proyecto, usuario=request.user, is_active=True).exists():
        return redirect('core:dashboard')

    if request.method == 'POST':
        if proyecto.creador == request.user:
            email_invitado = request.POST.get('email')
            rol_asignado = request.POST.get('rol')
            
            try:
                usuario_invitado = Usuario.objects.get(email=email_invitado)
                
                # ====================================================================
                # 🛡️ INICIO DEL BLOQUE TRANSACCIONAL (ACID)
                # ====================================================================
                with transaction.atomic():
                    MiembroProyecto.objects.update_or_create(
                        proyecto=proyecto, 
                        usuario=usuario_invitado,
                        defaults={'rol': rol_asignado}
                    )

                    if usuario_invitado != request.user:
                        sprint = Sprint.objects.filter(proyecto=proyecto, is_active=True).first()
                        if not sprint:
                            sprint = Sprint.objects.create(proyecto=proyecto, nombre="Sprint 1", is_active=True)
                        
                        tarea_bienvenida, created = Tarea.objects.get_or_create(
                            sprint=sprint,
                            titulo="HU-0: Lineamientos del Proyecto",
                            defaults={
                                'descripcion': "Espacio central para lineamientos generales del proyecto.",
                                'proposito': "Mantener a todos los miembros informados.",
                                'estado': 'Por Hacer',
                                'responsable': request.user
                            }
                        )

                        texto_bienvenida = f"¡Bienvenido al equipo @{usuario_invitado.username}! Revisa los lineamientos."
                        Evidencia.objects.create(
                            tarea=tarea_bienvenida,
                            autor=request.user,
                            comentario=texto_bienvenida
                        )
                        
                        Notificacion.objects.create(
                            usuario_mencionado=usuario_invitado,
                            autor_mencion=request.user,
                            tarea=tarea_bienvenida
                        )
                # ====================================================================
                # 🏁 FIN DEL BLOQUE TRANSACCIONAL
                # ====================================================================

                messages.success(request, f"¡Usuario {usuario_invitado.username} agregado exitosamente!")
                
            except Usuario.DoesNotExist:
                messages.error(request, "Error: No existe ningún usuario registrado con ese correo.")
            except Exception as e:
                messages.error(request, f"Error transaccional en el servidor: {str(e)}")
        
        return redirect('core:detalle_proyecto', proyecto_id=proyecto.id)

    miembros = proyecto.miembros.filter(is_active=True).select_related('usuario')
    return render(request, 'detalle_proyecto.html', {'proyecto': proyecto, 'miembros': miembros})


@login_required
def tablero_kanban(request, proyecto_id):
    """Vista principal que renderiza el tablero Kanban del proyecto."""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    sprints = Sprint.objects.filter(proyecto=proyecto, is_active=True).order_by('-id')
    sprint_actual = sprints.first()
    
    if sprint_actual:
        tareas = Tarea.objects.filter(sprint=sprint_actual, is_active=True)
    else:
        tareas = Tarea.objects.none()
        
    miembros = proyecto.miembros.filter(is_active=True).select_related('usuario')
    miembros_lista = [m.usuario.username for m in miembros]
    
    context = {
        'proyecto': proyecto,
        'por_hacer': tareas.filter(estado='Por Hacer'),
        'en_progreso': tareas.filter(estado='En Progreso'),
        'en_revision': tareas.filter(estado='En revisión'),
        'terminado': tareas.filter(estado='Terminado'),
        'sprints': sprints,
        'miembros': miembros,
        'miembros_json': miembros_lista,
    }
    return render(request, 'kanban.html', context)


@login_required
def crear_sprint(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST' and proyecto.creador == request.user:
        Sprint.objects.create(
            proyecto=proyecto, 
            nombre=request.POST.get('nombre'),
            fecha_inicio=request.POST.get('fecha_inicio'),
            fecha_fin=request.POST.get('fecha_fin')
        )
    return redirect('core:detalle_proyecto', proyecto_id=proyecto.id)


@login_required
def actualizar_estado_tarea(request):
    """Recibe la petición AJAX cuando se arrastra una tarjeta y actualiza la BD."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tarea = Tarea.objects.get(id=data['tarea_id'])
            tarea.estado = data['estado']
            tarea.save()
            return JsonResponse({'status': 'success', 'mensaje': 'Actualizado correctamente'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'mensaje': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def detalle_tarea_api(request, tarea_id):
    """Retorna toda la información de la tarea, incluyendo criterios y archivos adjuntos."""
    tarea = get_object_or_404(Tarea, id=tarea_id)
    evidencias = Evidencia.objects.filter(tarea=tarea).order_by('created_at')
    lista = [{
        'autor': e.autor.username, 
        'texto': e.comentario or "", 
        'archivo_url': e.archivo.url if e.archivo else None, 
        'archivo_nombre': e.archivo.name.split('/')[-1] if e.archivo else None, 
        'fecha': e.created_at.strftime("%d/%m %H:%M")
    } for e in evidencias]
    
    return JsonResponse({
        'id': tarea.id,
        'codigo': tarea.codigo,  # <-- NUEVO: Inyectamos el ID corto único para el JS
        'titulo': tarea.titulo,
        'descripcion': tarea.descripcion or 'Sin descripción detallada.',
        'proposito': tarea.proposito or 'Sin propósito definido.',
        'criterios_aceptacion': tarea.criterios_aceptacion or 'Sin criterios de aceptación.',
        'responsable': tarea.responsable.username if tarea.responsable else 'Sin asignar',
        'mensajes': lista
    })


@login_required
def agregar_evidencia_api(request, tarea_id):
    """Procesa textos y archivos subidos como evidencia y genera notificaciones por mención."""
    if request.method == 'POST':
        tarea = get_object_or_404(Tarea, id=tarea_id)
        texto_mensaje = request.POST.get('texto', '').strip()
        archivo = request.FILES.get('archivo')
        
        if texto_mensaje or archivo:
            evidencia = Evidencia.objects.create(
                tarea=tarea,
                autor=request.user,
                comentario=texto_mensaje,
                archivo=archivo
            )
            
            if texto_mensaje:
                candidatos_mencion = re.findall(r'@(\w+)', texto_mensaje)
                for username in candidatos_mencion:
                    try:
                        usuario_mencionado = Usuario.objects.get(username__iexact=username)
                        if usuario_mencionado != request.user:
                            Notificacion.objects.create(
                                usuario_mencionado=usuario_mencionado,
                                autor_mencion=request.user,
                                tarea=tarea
                            )
                    except Usuario.DoesNotExist:
                        continue
                        
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def crear_tarea(request, proyecto_id):
    """Vista para procesar el formulario incluyendo Propósitos y Criterios de Aceptación."""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        sprint_id = request.POST.get('sprint')
        responsable_id = request.POST.get('responsable')

        if titulo and sprint_id:
            sprint = get_object_or_404(Sprint, id=sprint_id, proyecto=proyecto)
            responsable = None
            if responsable_id:
                responsable = Usuario.objects.get(id=responsable_id)

            nueva_tarea = Tarea.objects.create(
                titulo=titulo,
                descripcion=request.POST.get('descripcion'),
                proposito=request.POST.get('proposito'),
                criterios_aceptacion=request.POST.get('criterios_aceptacion'),
                sprint=sprint,
                responsable=responsable,
                estado='Por Hacer'
            )
            
            if responsable and responsable != request.user:
                Notificacion.objects.create(
                    usuario_mencionado=responsable,
                    autor_mencion=request.user,
                    tarea=nueva_tarea
                )
            
    # CORREGIDO: Redirige consistentemente a la ruta del tablero del proyecto
    return redirect('core:tablero_kanban', proyecto_id=proyecto.id)


@login_required
def marcar_notificacion_leida_api(request, notificacion_id):
    """Marca una mención específica como leída."""
    if request.method == 'POST':
        notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario_mencionado=request.user)
        notificacion.leido = True
        notificacion.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def eliminar_tarea_api(request, tarea_id):
    """Permite al creador del proyecto eliminar una tarea."""
    if request.method == 'POST':
        tarea = get_object_or_404(Tarea, id=tarea_id)
        if tarea.sprint.proyecto.creador == request.user:
            tarea.delete()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'mensaje': 'No tienes permisos'}, status=403)
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def finalizar_proyecto(request, proyecto_id):
    """Permite al creador archivar/finalizar un proyecto."""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if proyecto.creador == request.user:
        proyecto.es_finalizado = True
        proyecto.save()
        messages.success(request, f"El proyecto '{proyecto.nombre}' ha sido finalizado con éxito.")
    else:
        messages.error(request, "No tienes permisos para finalizar este proyecto.")
    return redirect('core:dashboard')