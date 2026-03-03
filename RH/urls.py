from django.urls import path
from . import views as rh_views


urlpatterns = [
path('portal/', rh_views.portal, name='portal'),
path('portal/nova-advertencia/', rh_views.nova_advertencia, name='nova_advertencia'),
path('portal/cadastro-colaborador/', rh_views.cadastro_colaborador, name='cadastro_colaborador'),
]