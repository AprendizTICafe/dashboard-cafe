from django.contrib import admin
from django.urls import path, include
from dashboard import views
from dashboard import callback

urlpatterns = [
    path('', views.login_view, name='login'),
    path('auth/microsoft/login/', views.microsoft_login, name='microsoft_login'),
    path('auth/microsoft/callback/', callback.microsoft_callback, name='microsoft_callback'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls'))
]
