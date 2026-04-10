from django.urls import path
from . import views as ti_views

app_name = 'ti'

urlpatterns = [
path('advertências/', ti_views.advertencia, name='advertencia'),
path('advertencia/nova-advertencia/', ti_views.nova_advertencia, name='nova_advertencia'),
path('advertencia/<int:id>/detalhes/', ti_views.view_advertencia, name='view_advertencia'),
path('advertencia/<int:id>/enviar-rh/', ti_views.send_to_rh, name='send_to_rh'),
path('advertencia/excluir/<int:id>/', ti_views.excluir_advertencia, name='excluir_advertencia'),
]