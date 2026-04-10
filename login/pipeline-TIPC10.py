from django.contrib.auth.models import Group
from .services import fetch_full_user_data
from .models import Profile

def save_department(backend, user, response, *args, **kwargs):
    if 'azuread' in backend.name:
        token = response.get('access_token')
        
        if token: 
            full_data = fetch_full_user_data(token)
            
            if full_data:
                profile, created = Profile.objects.get_or_create(user=user)
                
                # Captura todos os dados do usuário
                profile.nome = full_data.get('givenName', '')
                profile.segundo_nome = full_data.get('surname', '')
                profile.email = full_data.get('mail', user.email)
                profile.office365_id = full_data.get('id', '')
                profile.ativo = full_data.get('accountEnabled', True)
                profile.numero = full_data.get('mobilePhone', '')
                profile.department = full_data.get('department', '')
                profile.cargo = full_data.get('jobTitle', '')
                
                profile.save()

                # Atualizar nome do usuário no User model também
                if profile.nome:
                    user.first_name = profile.nome
                if profile.segundo_nome:
                    user.last_name = profile.segundo_nome
                user.save()

                try:
                    if profile.department:
                        grupo = Group.objects.get(name=profile.department)
                        user.groups.add(grupo)
                except Group.DoesNotExist:
                    print(f"Aviso: Grupo '{profile.department}' não existe.")

                print(f">>> Sucesso! Usuário: {profile.nome} {profile.segundo_nome}")
                print(f">>> Email: {profile.email}")
                print(f">>> Office365ID: {profile.office365_id}")
                print(f">>> Departamento: {profile.department}")
                print(f">>> Ativo: {profile.ativo}")

                # Criar gestor conforme o departamento
                if profile.department in ['Tecnologia da Informação', 'TI']:
                    from TI.models import GestorTI
                    GestorTI.objects.get_or_create(
                        Email=profile.email,
                        defaults={
                            'Name': profile.nome,
                            'Office365ID': profile.office365_id,
                            'PhoneNumber': profile.numero,
                            'Active': profile.ativo
                        }
                    )
                    print(f">>> Usuário {user.username} roteado para o app TI.")
                    
                elif profile.department in ['Recursos Humanos', 'RH']:
                    from RH.models import GestorRH
                    GestorRH.objects.get_or_create(
                        Email=profile.email,
                        defaults={
                            'Name': profile.nome,
                            'Office365ID': profile.office365_id,
                            'PhoneNumber': profile.numero,
                            'Active': profile.ativo
                        }
                    )
                    print(f">>> Usuário {user.username} roteado para o app RH.")
                    
                elif profile.department in ['Diretoria', 'Gestão']:
                    from Diretoria.models import GestorDiretoria
                    GestorDiretoria.objects.get_or_create(
                        Email=profile.email,
                        defaults={
                            'Name': profile.nome,
                            'Office365ID': profile.office365_id,
                            'PhoneNumber': profile.numero,
                            'Active': profile.ativo
                        }
                    )
                    print(f">>> Usuário {user.username} roteado para app Diretoria.")
