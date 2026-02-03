from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import requests
import os
from dashboard.config import MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET, MICROSOFT_TENANT, REDIRECT_URI

def login_view(request):
    """Renderiza a página de login"""
    return render(request, 'tela_login.html')

@require_http_methods(["GET"])
def microsoft_login(request):
    """Inicia o fluxo de autenticação Microsoft"""
    # Gera a URL de autorização do Microsoft
    auth_url = f"https://login.microsoftonline.com/{MICROSOFT_TENANT}/oauth2/v2.0/authorize"
    
    params = {
        'client_id': MICROSOFT_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid profile email User.Read',
        'prompt': 'select_account'
    }
    
    # Monta a URL completa
    from urllib.parse import urlencode
    full_url = f"{auth_url}?{urlencode(params)}"
    # DEBUG: imprima a URL completa para verificar se redirect_uri está presente
    print('Microsoft authorize URL:', full_url)
    
    return redirect(full_url)

@login_required(login_url='login')
def dashboard_view(request):
    """Renderiza o dashboard após login"""
    context = {
        'user': request.user,
        'nome_completo': f"{request.user.first_name} {request.user.last_name}".strip()
    }
    return render(request, 'dashboard.html', context)
