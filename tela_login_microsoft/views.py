from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .models import Advertencia

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

def painel_view(request):
    user = request.user
    
    # Se o usuário for superusuário ou do RH central, vê tudo
    # Caso contrário, filtra pelo departamento do gestor
    if user.is_superuser or user.groups.filter(name='RH_Central').exists():
        advertencias_queryset = Advertencia.objects.all()
    else:
        # Filtra advertências onde o solicitante é o usuário logado 
        # OU o departamento é o mesmo do usuário
        advertencias_queryset = Advertencia.objects.filter(solicitante=user)

    # Estatísticas baseadas no QuerySet filtrado
    context = {
        'total_advertencias': advertencias_queryset.count(),
        'advertencias_pendentes': advertencias_queryset.filter(status='Solicitada').count(),
        'advertencias_rejeitadas': advertencias_queryset.filter(status='Em Análise RH').count(),
        'advertencias_em_analise': advertencias_queryset.filter(status='Em Análise Diretoria').count(),
        'advertencias_aprovadas': advertencias_queryset.filter(status='Aprovada').count(),
        'advertencias_concluidas': advertencias_queryset.filter(status='Concluída').count(),
        'ultimas_advertencias': advertencias_queryset.order_by('-data_solicitacao')[:5],
    }
    
    return render(request, 'base.html', context)
