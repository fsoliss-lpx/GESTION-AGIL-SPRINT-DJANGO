# backend/core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Proyecto, MiembroProyecto, Sprint, Tarea, Evidencia

@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    # Ya no mostramos 'rol' porque ahora depende del proyecto
    list_display = ('username', 'email', 'is_staff', 'is_active')

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'creador', 'created_at', 'is_active')
    search_fields = ('nombre',)

@admin.register(MiembroProyecto)
class MiembroProyectoAdmin(admin.ModelAdmin):
    list_display = ('proyecto', 'usuario', 'rol', 'is_active')
    list_filter = ('proyecto', 'rol')

@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'proyecto', 'fecha_inicio', 'fecha_fin', 'estado', 'is_active')
    list_filter = ('estado', 'proyecto')

@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'sprint', 'responsable', 'estado', 'is_active')
    list_filter = ('estado', 'sprint__proyecto', 'responsable')
    search_fields = ('titulo',)

@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = ('tarea', 'autor', 'created_at', 'is_active')
