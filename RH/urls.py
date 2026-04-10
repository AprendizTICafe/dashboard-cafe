from django.urls import path
from . import views as rh_views

app_name = 'rh'

urlpatterns = [
path('advertencias/', rh_views.advertencia, name='advertencia'),
path('advertencia/nova-advertencia/', rh_views.nova_advertencia, name='nova_advertencia'),
path('advertencia/cadastro-colaborador/', rh_views.cadastro_colaborador, name='cadastro_colaborador'),
]