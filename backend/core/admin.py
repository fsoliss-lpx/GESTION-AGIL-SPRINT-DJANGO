from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Sprint, Tarea

# Registramos el modelo de Usuario personalizado
@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'rol', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Rol en Scrum', {'fields': ('rol',)}),
    )

@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'estado', 'is_active')
    list_filter = ('estado', 'is_active')

@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'sprint', 'responsable', 'estado', 'is_active')
    list_filter = ('estado', 'sprint', 'responsable')
