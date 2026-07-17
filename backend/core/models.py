import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_active', 'deleted_at', 'updated_at'])

# 1. USUARIO (Ya no tiene el rol global)
class Usuario(AbstractUser):
    """Modelo de usuario base para el login."""
    def __str__(self):
        return self.username

# 2. PROYECTO
class Proyecto(BaseModel):
    """Agrupa los Sprints y define el equipo de trabajo."""
    nombre = models.CharField('Nombre del Proyecto', max_length=150)
    descripcion = models.TextField('Descripción', blank=True, null=True)
    # CORREGIDO AQUÍ:
    creador = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='proyectos_creados')
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    es_finalizado = models.BooleanField(default=False)
    
    def __str__(self):
        return self.nombre

# 3. MIEMBROS DEL PROYECTO (Aquí definimos los roles)
class MiembroProyecto(BaseModel):
    ROLES_CHOICES = [
        ('PO', 'Product Owner'),
        ('SM', 'Scrum Master'),
        ('DEV', 'Desarrollador'),
    ]
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='miembros')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='proyectos_asignados')
    rol = models.CharField('Rol', max_length=20, choices=ROLES_CHOICES, default='DEV')

    class Meta:
        unique_together = ('proyecto', 'usuario') # Un usuario no puede estar 2 veces en el mismo proyecto

    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()} en {self.proyecto.nombre}"

# 4. SPRINT (Ahora pertenece a un Proyecto)
class Sprint(BaseModel):
    ESTADOS_CHOICES = [
        ('Planificado', 'Planificado'),
        ('Activo', 'Activo'),
        ('Terminado', 'Terminado'),
    ]
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='sprints')
    nombre = models.CharField('Nombre', max_length=100)
    fecha_inicio = models.DateField('Fecha de inicio')
    fecha_fin = models.DateField('Fecha de fin')
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS_CHOICES, default='Planificado')

    def __str__(self):
        return f"{self.nombre} ({self.proyecto.nombre})"

# 5. TAREA (Historia de Usuario)
class Tarea(BaseModel): # Hereda de BaseModel para tener created_at, updated_at, etc.
    ESTADOS = (
        ('Por Hacer', 'Por Hacer'),
        ('En Progreso', 'En Progreso'),
        ('En revisión', 'En revisión'),
        ('Terminado', 'Terminado'),
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    proposito = models.TextField(blank=True, null=True)
    criterios_aceptacion = models.TextField(blank=True, null=True)
    codigo = models.CharField(max_length=10, unique=True, blank=True, null=True)
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Por Hacer')
    sprint = models.ForeignKey('Sprint', on_delete=models.CASCADE, related_name='tareas')
    responsable = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_asignadas')
    # Ya no necesitas declarar is_active aquí porque BaseModel ya lo trae

    def save(self, *args, **kwargs):
        if not self.codigo:
            # Genera un string de 8 caracteres (ej: 86e23ax1)
            self.codigo = uuid.uuid4().hex[:8].lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo

# 6. EVIDENCIAS / COMENTARIOS (Para las imágenes y chat de la tarea)
class Evidencia(BaseModel):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='evidencias')
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    comentario = models.TextField('Comentario', blank=True, null=True)
    archivo = models.FileField(upload_to='evidencias/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidencia de {self.autor.username} en {self.tarea.titulo}"
    

class Notificacion(models.Model):
    """Registra las menciones (@usuario) generadas en los chats de las tareas."""
    usuario_mencionado = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    autor_mencion = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='menciones_hechas')
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='notificaciones')
    created_at = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Mención a {self.usuario_mencionado.username} en {self.tarea.titulo}"