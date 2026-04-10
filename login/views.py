from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.views.decorators.cache import never_cache


# --- SIGNALS ---
@never_cache
@receiver(post_save, sender=User)
def cadastrar_usuario_no_grupo(sender, instance, created, **kwargs):
    """
    Nota: Este signal só funcionará se o Profile for criado ANTES 
    ou se houver um delay. O ideal é disparar isso no save do Profile.
    """
    if created:
        try:
            # Tenta pegar o perfil. Se o perfil for criado via signal também,
            # pode haver um erro de timing aqui.
            if hasattr(instance, 'profile'):
                nome_do_grupo = instance.profile.department
                if nome_do_grupo:
                    grupo, _ = Group.objects.get_or_create(name=nome_do_grupo)
                    instance.groups.add(grupo)
        except Exception as e:
            print(f"Erro no signal: {e}")

# --- VIEWS ---
@never_cache
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
    return render(request, 'base.html', {'user': request.user})
