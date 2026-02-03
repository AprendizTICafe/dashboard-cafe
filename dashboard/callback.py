from django.shortcuts import redirect
from django.contrib.auth import login
from django.views.decorators.http import require_http_methods
import requests
import os
from dashboard.config import MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET, MICROSOFT_TENANT, REDIRECT_URI


@require_http_methods(["GET"])
def microsoft_callback(request):
    """
    Callback que recebe a resposta da Microsoft.
    """
    code = request.GET.get('code')
    error = request.GET.get('error')

    if error:
        error_description = request.GET.get('error_description', 'Erro desconhecido')
        return redirect(f'/?error={error_description}')

    if not code:
        return redirect('/?error=No authorization code received')

    try:
        token_url = f"https://login.microsoftonline.com/{MICROSOFT_TENANT}/oauth2/v2.0/token"

        token_data = {
            'client_id': MICROSOFT_CLIENT_ID,
            'client_secret': MICROSOFT_CLIENT_SECRET,
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'
        }

        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_json = token_response.json()

        access_token = token_json.get('access_token')
        if not access_token:
            return redirect('/?error=Failed to get access token')

        user_info_url = 'https://graph.microsoft.com/v1.0/me'
        headers = {'Authorization': f'Bearer {access_token}'}

        user_response = requests.get(user_info_url, headers=headers)
        user_response.raise_for_status()
        user_data = user_response.json()

        email = user_data.get('userPrincipalName') or user_data.get('mail')
        first_name = user_data.get('givenName', '')
        last_name = user_data.get('surname', '')

        if not email:
            return redirect('/?error=Could not retrieve email from Microsoft')

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

        return redirect('/dashboard/')

    except requests.exceptions.RequestException as e:
        return redirect(f'/?error=Authentication failed: {str(e)}')
    except Exception as e:
        return redirect(f'/?error=An error occurred: {str(e)}')
