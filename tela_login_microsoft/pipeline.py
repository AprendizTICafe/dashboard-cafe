def save_department(backend, user, response, *args, **kwargs):
    # Usar 'in' garante que pegue qualquer variação do nome do backend Azure
    if 'azuread' in backend.name:
        dept = response.get('department')
        
        # Log para você ver no terminal se o dado está chegando
        print(f"--- DEBUG PIPELINE ---")
        print(f"Backend: {backend.name}")
        print(f"Response data: {response}") 
        
        if dept:
            from .models import Profile
            profile, created = Profile.objects.get_or_create(user=user)
            profile.department = dept
            profile.save()
            print(f"Departamento {dept} salvo com sucesso!")