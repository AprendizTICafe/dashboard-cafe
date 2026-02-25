from django.urls import path
from . import views as rh_views


urlpatterns = [
path('rh/advertencias/', rh_views.advertencias, name='advertencias'),
path('nova-advertencia/', rh_views.nova_advertencia, name='nova_advertencia'),
path('acompanhar-advertencias/', rh_views.acompanhar_advertencias, name='acompanhar_advertencias'),
]