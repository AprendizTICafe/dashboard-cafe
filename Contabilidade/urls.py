from django.urls import path
from . import views as contabilidade_views

app_name = 'contabilidade'

urlpatterns = [
path('advertências/', contabilidade_views.advertencia, name='advertencia'),
path('advertencia/nova-advertencia/', contabilidade_views.nova_advertencia, name='nova_advertencia'),
path('advertencia/<int:id>/detalhes/', contabilidade_views.view_advertencia, name='view_advertencia'),
path('advertencia/<int:id>/enviar-rh/', contabilidade_views.send_to_rh, name='send_to_rh'),
path('advertencia/excluir/<int:id>/', contabilidade_views.excluir_advertencia, name='excluir_advertencia'),
]