from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('crear-proyecto/', views.crear_proyecto, name='crear_proyecto'),
    path('proyecto/<int:proyecto_id>/', views.detalle_proyecto, name='detalle_proyecto'),
    path('proyecto/<int:proyecto_id>/tablero/', views.tablero_kanban, name='tablero'),
    path('api/actualizar-tarea/', views.actualizar_estado_tarea, name='actualizar_tarea'),
    path('api/tarea/<int:tarea_id>/', views.detalle_tarea_api, name='detalle_tarea_api'),
    path('api/tarea/<int:tarea_id>/evidencia/', views.agregar_evidencia_api, name='agregar_evidencia_api'),
]
