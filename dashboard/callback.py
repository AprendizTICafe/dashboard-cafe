from django.shortcuts import redirect
from django.contrib.auth import login
from django.views.decorators.http import require_http_methods
from django.urls import reverse
import requests
import os
import logging


logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def microsoft_callback(request):
    """
    Callback que recebe a resposta da Microsoft.
    Autentica o usuário e o redireciona para o dashboard.
    """
    code = request.GET.get('code')
    error = request.GET.get('error')

    login_url = reverse('login')

    if error:
        error_description = request.GET.get('error_description', 'Erro desconhecido')
        logger.warning(f'Microsoft OAuth error: {error} - {error_description}')
        return redirect(f'{login_url}?error={error_description}')

    if not code:
        logger.error('No authorization code received from Microsoft')
        return redirect(f'{login_url}?error=No authorization code received')

    try:
        token_url = f"https://login.microsoftonline.com/familiadositio.com.br/oauth2/v2.0/token"

        token_data = {
            'client_id': '0c1c7c9c-c1f7-431c-a238-1b53a950a9d6',
            'client_secret': 'YC78Q~aywRIVtnK8Y0rcNG6BobC8js146-pLWbxg',
            'code': code,
            'redirect_uri': 'https://10.61.1.193/auth/microsoft/callback/',
            'grant_type': 'authorization_code'
        }

        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_json = token_response.json()

        access_token = token_json.get('access_token')
        if not access_token:
            logger.error('Failed to get access token from Microsoft')
            return redirect(f'{login_url}?error=Failed to get access token')

        user_info_url = 'https://graph.microsoft.com/v1.0/me'
        headers = {'Authorization': f'Bearer {access_token}'}

        user_response = requests.get(user_info_url, headers=headers)
        user_response.raise_for_status()
        user_data = user_response.json()

        email = user_data.get('userPrincipalName') or user_data.get('mail')
        first_name = user_data.get('givenName', '')
        last_name = user_data.get('surname', '')

        if not email:
            logger.error('Could not retrieve email from Microsoft')
            return redirect(f'{login_url}?error=Could not retrieve email from Microsoft')

        from django.contrib.auth.models import User

        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            }
        )

        if not created:
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        logger.info(f'User {email} successfully authenticated via Microsoft')

        return redirect('dashboard')

    except requests.exceptions.RequestException as e:
        logger.error(f'Request error during Microsoft authentication: {str(e)}')
        return redirect(f'{login_url}?error=Authentication failed: {str(e)}')
    except Exception as e:
        logger.error(f'Unexpected error during Microsoft authentication: {str(e)}')
        return redirect(f'{login_url}?error=An error occurred: {str(e)}')
