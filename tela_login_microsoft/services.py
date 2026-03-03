import requests

def fetch_full_user_data(access_token):
    url = "https://graph.microsoft.com/v1.0/me?$select=department"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # VAMOS OLHAR TUDO NO TERMINAL
        print("--- CONTEÚDO BRUTO DA MICROSOFT ---")
        for chave, valor in data.items():
            print(f"{chave}: {valor}")
        return data
    return None