import requests

def fetch_full_user_data(access_token):
    """
    Busca dados completos do usuário do Microsoft Azure AD
    
    Campos retornados:
    - givenName: Nome
    - surname: Segundo nome
    - mail: Email
    - id: Office365ID
    - accountEnabled: Status ativo/inativo
    - department: Departamento
    - mobilePhone: Número de telefone
    """
    url = "https://graph.microsoft.com/v1.0/me?$select=givenName,surname,mail,id,accountEnabled,department,mobilePhone"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("--- DADOS DO USUÁRIO MICROSOFT ---")
            for chave, valor in data.items():
                print(f"{chave}: {valor}")
            return data
        else:
            print(f"Erro ao buscar dados do usuário: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None