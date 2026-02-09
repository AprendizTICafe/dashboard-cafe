from django.contrib import admin
from django.urls import path, include
from dashboard import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls'))
]
