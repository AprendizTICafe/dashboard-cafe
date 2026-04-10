from django.urls import path
from . import views as marketing_views

app_name = 'marketing'

urlpatterns = [
path('advertências/', marketing_views.advertencia, name='advertencia'),
path('advertencia/nova-advertencia/', marketing_views.nova_advertencia, name='nova_advertencia'),
path('advertencia/<int:id>/detalhes/', marketing_views.view_advertencia, name='view_advertencia'),
path('advertencia/<int:id>/enviar-rh/', marketing_views.send_to_rh, name='send_to_rh'),
path('advertencia/excluir/<int:id>/', marketing_views.excluir_advertencia, name='excluir_advertencia'),
]