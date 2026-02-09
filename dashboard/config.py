from dotenv import load_dotenv
import os

load_dotenv()

# Microsoft OAuth configuration read from environment
MICROSOFT_CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID')
MICROSOFT_CLIENT_SECRET = os.getenv('MICROSOFT_CLIENT_SECRET')
MICROSOFT_TENANT = os.getenv('MICROSOFT_TENANT', 'familiadositio.com.br')
# IMPORTANTE: Este redirect_uri DEVE ser registrado exatamente igual no Azure AD
MICROSOFT_REDIRECT_URI = os.getenv('MICROSOFT_REDIRECT_URI', 'https://10.61.1.193/auth/microsoft/callback/')
