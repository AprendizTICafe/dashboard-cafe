from django.urls import path
from . import views as ti_views

app_name = 'ti'

urlpatterns = [
path('advertências/', ti_views.advertencia, name='advertencia'),
path('advertencia/nova-advertencia/', ti_views.nova_advertencia, name='nova_advertencia'),
path('advertencia/excluir/<int:id>/', ti_views.excluir_advertencia, name='excluir_advertencia'),
]