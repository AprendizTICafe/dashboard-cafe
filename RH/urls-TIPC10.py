from django.urls import path
from . import views as rh_views

app_name = 'rh'

urlpatterns = [
path('advertencias/', rh_views.advertencia, name='advertencia'),
path('advertencia/cadastro-colaborador/', rh_views.cadastro_colaborador, name='cadastro_colaborador'),
path('advertencia/<int:id>/detalhes/', rh_views.view_advertencia_rh, name='view_advertencia_rh'),
path('advertencia/<int:id>/editar/', rh_views.edit_advertencia, name='edit_advertencia'),
path('advertencia/<int:id>/enviar-diretoria/', rh_views.send_to_diretoria, name='send_to_diretoria'),
path('advertencia/<int:id>/iniciar-investigacao/', rh_views.start_investigation, name='start_investigation'),
path('advertencia/<int:id>/agendar-e-concluir/', rh_views.schedule_and_conclude, name='schedule_and_conclude'),
path('advertencia/<int:id>/sindicancia/', rh_views.handle_sindicancia, name='handle_sindicancia'),
path('advertencia/<int:id>/enviar-sindicancia-diretoria/', rh_views.send_sindicancia_to_diretoria, name='send_sindicancia_to_diretoria'),
path('advertencia/<int:id>/download-pdf/', rh_views.download_pdf_advertencia, name='download_pdf'),
]