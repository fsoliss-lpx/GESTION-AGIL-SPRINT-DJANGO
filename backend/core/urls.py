from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Autenticación y Dashboard
    path('registro/', views.registro, name='registro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Gestión de Proyectos y Sprints
    path('crear-proyecto/', views.crear_proyecto, name='crear_proyecto'),
    path('proyecto/<int:proyecto_id>/', views.detalle_proyecto, name='detalle_proyecto'),
    path('proyecto/<int:proyecto_id>/crear-sprint/', views.crear_sprint, name='crear_sprint'),
    
    # Tablero Kanban y Tareas
    path('proyecto/<int:proyecto_id>/tablero/', views.tablero_kanban, name='tablero'),
    path('proyecto/<int:proyecto_id>/crear-tarea/', views.crear_tarea, name='crear_tarea'),
    
    # APIs (AJAX y Panel Lateral)
    path('api/actualizar-tarea/', views.actualizar_estado_tarea, name='actualizar_tarea'),
    path('api/tarea/<int:tarea_id>/', views.detalle_tarea_api, name='detalle_tarea_api'),
    
    # CORREGIDO: Se añade la barra '/' al final para evitar fallos con el Fetch de JS
    path('api/tarea/<int:tarea_id>/evidencia/', views.agregar_evidencia_api, name='agregar_evidencia_api'),
    
    path('api/notificacion/<int:notificacion_id>/leer/', views.marcar_notificacion_leida_api, name='marcar_leida_api'),
    path('api/tarea/<int:tarea_id>/eliminar/', views.eliminar_tarea_api, name='eliminar_tarea'),
    path('proyecto/<int:proyecto_id>/finalizar/', views.finalizar_proyecto, name='finalizar_proyecto'),
]
