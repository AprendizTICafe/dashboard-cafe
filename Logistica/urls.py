from django.urls import path
from . import views as logistica_views

app_name = 'logistica'

urlpatterns = [
path('advertências/', logistica_views.advertencia, name='advertencia'),
path('advertencia/nova-advertencia/', logistica_views.nova_advertencia, name='nova_advertencia'),
path('advertencia/<int:id>/detalhes/', logistica_views.view_advertencia, name='view_advertencia'),
path('advertencia/<int:id>/enviar-rh/', logistica_views.send_to_rh, name='send_to_rh'),
path('advertencia/excluir/<int:id>/', logistica_views.excluir_advertencia, name='excluir_advertencia'),
]