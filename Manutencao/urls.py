from django.urls import path
from . import views as manutencao_views

app_name = 'manutencao'

urlpatterns = [
path('advertências/', manutencao_views.advertencia, name='advertencia'),
path('advertencia/nova-advertencia/', manutencao_views.nova_advertencia, name='nova_advertencia'),
path('advertencia/<int:id>/detalhes/', manutencao_views.view_advertencia, name='view_advertencia'),
path('advertencia/<int:id>/enviar-rh/', manutencao_views.send_to_rh, name='send_to_rh'),
path('advertencia/excluir/<int:id>/', manutencao_views.excluir_advertencia, name='excluir_advertencia'),
]