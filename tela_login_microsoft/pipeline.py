from .services import fetch_full_user_data
from .models import Profile

def save_department(backend, user, response, *args, **kwargs):
    if 'azuread' in backend.name:
        token = response.get('access_token')
        
        if token and '.' in token:
            full_data = fetch_full_user_data(token)
            
            if full_data:
                profile, _ = Profile.objects.get_or_create(user=user)
                
                # Captura o departamento do novo JSON com Select
                dept = full_data.get('department')
                profile.department = dept if dept else "Não Informado"
                
                profile.save()
                print(f">>> Departamento final salvo no banco: {profile.department}")