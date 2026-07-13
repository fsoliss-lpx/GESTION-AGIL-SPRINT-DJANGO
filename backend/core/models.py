from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class SoftDeleteManager(models.Manager):
    """Manager que excluye automáticamente registros con is_active=False."""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class BaseModel(models.Model):
    """Clase abstracta base con campos de auditoría y soft delete."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self):
        """Marca el registro como eliminado (sin borrarlo físicamente)."""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_active', 'deleted_at', 'updated_at'])

    def restore(self):
        """Restaura un registro eliminado."""
        self.is_active = True
        self.deleted_at = None
        self.save(update_fields=['is_active', 'deleted_at', 'updated_at'])

class Usuario(AbstractUser):
    """Modelo de usuario que extiende el nativo de Django para incluir roles Scrum."""
    ROLES_CHOICES = [
        ('PO', 'Product Owner'),
        ('SM', 'Scrum Master'),
        ('DEV', 'Desarrollador'),
    ]
    rol = models.CharField('Rol', max_length=20, choices=ROLES_CHOICES, default='DEV')

    def __str__(self):
        return self.username

class Sprint(BaseModel):
    """Iteraciones de trabajo bajo la metodología Scrum."""
    ESTADOS_CHOICES = [
        ('Planificado', 'Planificado'),
        ('Activo', 'Activo'),
        ('Terminado', 'Terminado'),
    ]
    nombre = models.CharField('Nombre', max_length=100)
    fecha_inicio = models.DateField('Fecha de inicio')
    fecha_fin = models.DateField('Fecha de fin')
    objetivo = models.TextField('Objetivo')
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS_CHOICES, default='Planificado')

    def __str__(self):
        return self.nombre

class Tarea(BaseModel):
    """Historias de usuario o requerimientos técnicos."""
    ESTADOS_CHOICES = [
        ('Por Hacer', 'Por Hacer'),
        ('En Progreso', 'En Progreso'),
        ('Terminado', 'Terminado'),
    ]
    titulo = models.CharField('Título', max_length=150)
    descripcion = models.TextField('Descripción')
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS_CHOICES, default='Por Hacer')
    
    # Relaciones (Llaves foráneas)
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE, related_name='tareas')
    responsable = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_asignadas')

    def __str__(self):
        return self.titulo