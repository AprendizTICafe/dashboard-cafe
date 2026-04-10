from django.urls import path
from . import views as financeiro_views

app_name = 'financeiro'

urlpatterns = [
path('advertências/', financeiro_views.advertencia, name='advertencia'),
path('advertencia/nova-advertencia/', financeiro_views.nova_advertencia, name='nova_advertencia'),
path('advertencia/<int:id>/detalhes/', financeiro_views.view_advertencia, name='view_advertencia'),
path('advertencia/<int:id>/enviar-rh/', financeiro_views.send_to_rh, name='send_to_rh'),
path('advertencia/excluir/<int:id>/', financeiro_views.excluir_advertencia, name='excluir_advertencia'),
]