from django.contrib import admin
from django.urls import path, include
from tela_login_microsoft import views as tela_views
from django.contrib.auth import views as auth_views
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
    
]