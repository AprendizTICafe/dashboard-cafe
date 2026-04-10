from django.urls import path
from . import views as diretoria_views

app_name = 'diretoria'

urlpatterns = [
    path('advertencias/', diretoria_views.advertencia, name='advertencia'),
    path('advertencia/<int:id>/detalhes/', diretoria_views.view_advertencia_diretoria, name='view_advertencia_diretoria'),
    path('advertencia/<int:id>/aprovar/', diretoria_views.approve_advertencia, name='approve_advertencia'),
    path('advertencia/<int:id>/devolver-sindicancia/', diretoria_views.return_to_investigation, name='return_to_investigation'),
    path('advertencia/<int:id>/download-pdf/', diretoria_views.download_pdf_advertencia, name='download_pdf'),
]
