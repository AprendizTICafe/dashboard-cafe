from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def index_view(request):
    """Redireciona para dashboard se autenticado, caso contrário para login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

def login_view(request):
    """Renderiza a página de login"""
    return render(request, 'tela_login.html')

@login_required(login_url='login')
def dashboard_view(request):
    """Renderiza o dashboard após login"""
    context = {
        'user': request.user,
        'nome_completo': f"{request.user.first_name} {request.user.last_name}".strip()
    }
    return render(request, 'dashboard.html', context)
