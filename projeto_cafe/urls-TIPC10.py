from django.contrib import admin
from django.urls import path, include
from login import views as tela_views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Social Auth (Microsoft/Azure AD)
    path('oauth/', include('social_django.urls', namespace='social')),
    # Login customizado (com botão Microsoft e formulário)
    path('login/', tela_views.login_view, name='login'),
    # Logout padrão do Django
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Dashboard protegido
    path('', tela_views.base, name='base'),
    path('rh/', include('RH.urls')),
    path('ti/', include('TI.urls')),
    path('diretoria/', include('Diretoria.urls')),
    path('contabilidade/', include('Contabilidade.urls')),
    path('financeiro/', include('Financeiro.urls')),
    path('logistica/', include('Logistica.urls')),
    path('manutencao/', include('Manutencao.urls')),
    path('marketing/', include('Marketing.urls')),
    path('segurancatrabalho/', include('SegurancaTrabalho.urls')),
]

# Servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)