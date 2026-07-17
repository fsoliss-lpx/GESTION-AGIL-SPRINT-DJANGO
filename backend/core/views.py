import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Tarea, Proyecto, MiembroProyecto, Usuario
from .forms import RegistroUsuarioForm

def registro(request):
    """Vista para que nuevos usuarios creen su cuenta y entren al sistema."""
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:dashboard')
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'registro.html', {'form': form})

@login_required
def dashboard(request):
    """Vista del panel de proyectos estilo SaaS."""
    proyectos_creados = Proyecto.objects.filter(creador=request.user, is_active=True)
    
    ids_proyectos_miembro = MiembroProyecto.objects.filter(usuario=request.user, is_active=True).values_list('proyecto_id', flat=True)
    proyectos_miembro = Proyecto.objects.filter(id__in=ids_proyectos_miembro, is_active=True)
    
    proyectos = (proyectos_creados | proyectos_miembro).distinct()
    return render(request, 'dashboard.html', {'proyectos': proyectos})

@login_required
def crear_proyecto(request):
    """Vista para registrar un nuevo proyecto y asignar al creador como PO."""
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        
        if nombre:
            nuevo_proyecto = Proyecto.objects.create(
                nombre=nombre, 
                descripcion=descripcion, 
                creador=request.user
            )
            MiembroProyecto.objects.create(
                proyecto=nuevo_proyecto,
                usuario=request.user,
                rol='PO'
            )
            return redirect('core:dashboard')
            
    return render(request, 'crear_proyecto.html')

@login_required
def detalle_proyecto(request, proyecto_id):
    """Vista para gestionar el equipo del proyecto."""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    if not MiembroProyecto.objects.filter(proyecto=proyecto, usuario=request.user, is_active=True).exists():
        return redirect('core:dashboard')

    if request.method == 'POST':
        if proyecto.creador == request.user:
            email_invitado = request.POST.get('email')
            rol_asignado = request.POST.get('rol')
            
            try:
                usuario_invitado = Usuario.objects.get(email=email_invitado)
                MiembroProyecto.objects.update_or_create(
                    proyecto=proyecto, 
                    usuario=usuario_invitado,
                    defaults={'rol': rol_asignado}
                )
                messages.success(request, f"¡Usuario {usuario_invitado.username} agregado exitosamente como {rol_asignado}!")
            except Usuario.DoesNotExist:
                messages.error(request, "Error: No existe ningún usuario registrado con ese correo.")
        
        return redirect('core:detalle_proyecto', proyecto_id=proyecto.id)

    miembros = proyecto.miembros.filter(is_active=True).select_related('usuario')
    return render(request, 'detalle_proyecto.html', {'proyecto': proyecto, 'miembros': miembros})

@login_required
def tablero_kanban(request, proyecto_id):
    """Vista principal que renderiza el tablero Kanban del proyecto."""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    
    tareas = Tarea.objects.filter(sprint__proyecto=proyecto, is_active=True)
    
    context = {
        'proyecto': proyecto,
        'por_hacer': tareas.filter(estado='Por Hacer'),
        'en_progreso': tareas.filter(estado='En Progreso'),
        'en_revision': tareas.filter(estado='En revisión'),
        'terminado': tareas.filter(estado='Terminado'),
    }
    return render(request, 'kanban.html', context)

@login_required
def actualizar_estado_tarea(request):
    """Recibe la petición AJAX cuando se arrastra una tarjeta y actualiza la BD."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tarea = Tarea.objects.get(id=data['tarea_id'])
            tarea.estado = data['estado'] # Sincronizado con Javascript
            tarea.save()
            return JsonResponse({'status': 'success', 'mensaje': 'Actualizado correctamente'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'mensaje': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

# backend/core/views.py (Agrega al final)

@login_required
def detalle_tarea_api(request, tarea_id):
    """API para obtener detalles de la tarea y su historial de chat/evidencias."""
    tarea = get_object_or_404(Tarea, id=tarea_id)
    evidencias = Evidencia.objects.filter(tarea=tarea).select_related('autor').order_by('created_at')
    
    lista_mensajes = []
    for ev in evidencias:
        # Extraemos el texto de la evidencia sin importar cómo se llame el campo
        texto = getattr(ev, 'comentario', getattr(ev, 'descripcion', getattr(ev, 'texto', '')))
        lista_mensajes.append({
            'autor': ev.autor.username,
            'texto': texto,
            'fecha': ev.created_at.strftime("%d/%m %H:%M")
        })

    return JsonResponse({
        'id': tarea.id,
        'titulo': tarea.titulo,
        'descripcion': getattr(tarea, 'descripcion', 'Sin descripción detallada.'),
        'responsable': tarea.responsable.username if tarea.responsable else 'Sin asignar',
        'mensajes': lista_mensajes
    })

@login_required
def agregar_evidencia_api(request, tarea_id):
    """API para guardar un nuevo mensaje en la tarea."""
    if request.method == 'POST':
        data = json.loads(request.body)
        tarea = get_object_or_404(Tarea, id=tarea_id)
        texto_mensaje = data.get('texto', '').strip()
        
        if texto_mensaje:
            # Intentamos guardar el mensaje detectando el nombre de tu columna
            try:
                Evidencia.objects.create(tarea=tarea, autor=request.user, comentario=texto_mensaje)
            except TypeError:
                try:
                    Evidencia.objects.create(tarea=tarea, autor=request.user, descripcion=texto_mensaje)
                except TypeError:
                    Evidencia.objects.create(tarea=tarea, autor=request.user, texto=texto_mensaje)
                    
            return JsonResponse({'status': 'success'})
            
    return JsonResponse({'status': 'error'}, status=400)