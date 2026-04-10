from django.contrib.auth.models import Group
from .services import fetch_full_user_data
from .models import Profile
from TI.models import Gestor as GestorID 

def save_department(backend, user, response, *args, **kwargs):
    if 'azuread' in backend.name:
        token = response.get('access_token')
        
        if token: 
            full_data = fetch_full_user_data(token)
            
            if full_data:
                profile, created = Profile.objects.get_or_create(user=user)
                dept_nome = full_data.get('department')
                profile.department = dept_nome
                profile.save()

                try:
                    grupo = Group.objects.get(name=dept_nome)
                    user.groups.add(grupo)
                except Group.DoesNotExist:
                    print(f"Aviso: Grupo '{dept_nome}' não existe.")

                print(f">>> Sucesso! Depto: {dept_nome} salvo no Profile")

                if dept_nome in ['Tecnologia da Informação']:
                    
                    GestorID.objects.get_or_create(Name=user, Email=user.email, Department=dept_nome)
                    
                    print(f">>> Usuário {user.username} roteado para o app TI.")