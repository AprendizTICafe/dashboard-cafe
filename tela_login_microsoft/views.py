from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('base')
        else:
            return render(request, 'tela_oauth/login.html', {'error': 'Usuário ou senha inválidos.'})
    return render(request, 'tela_oauth/login.html')

@login_required
def base(request):
    # O objeto 'user' está disponível no request após o OAuth
    return render(request, 'base.html', {
        'user': request.user
    })
