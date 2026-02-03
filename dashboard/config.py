from dotenv import load_dotenv
import os

load_dotenv()

# Microsoft OAuth configuration read from environment
MICROSOFT_CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID')
MICROSOFT_CLIENT_SECRET = os.getenv('MICROSOFT_SECRET')
MICROSOFT_TENANT = os.getenv('MICROSOFT_TENANT', 'organizations')
REDIRECT_URI = os.getenv('MICROSOFT_REDIRECT_URI', 'http://127.0.0.1:8000/auth/microsoft/callback/')
