from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def login_view(request):
    # Se o usuário já estiver logado, manda direto para o Painel
    if request.user.is_authenticated:
        return redirect('base')
    return render(request, 'tela_oauth/login.html')

@login_required
def base(request):
    return render(request, 'base.html', {
        'user': request.user
    })
