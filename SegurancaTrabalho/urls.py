from django.urls import path
from . import views as segurancatrabalho_views

app_name = 'segurancatrabalho'

urlpatterns = [
path('advertências/', segurancatrabalho_views.advertencia, name='advertencia'),
path('advertencia/nova-advertencia/', segurancatrabalho_views.nova_advertencia, name='nova_advertencia'),
path('advertencia/<int:id>/detalhes/', segurancatrabalho_views.view_advertencia, name='view_advertencia'),
path('advertencia/<int:id>/enviar-rh/', segurancatrabalho_views.send_to_rh, name='send_to_rh'),
path('advertencia/excluir/<int:id>/', segurancatrabalho_views.excluir_advertencia, name='excluir_advertencia'),
]
