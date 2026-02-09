import os 
from dotenv import load_dotenv

load_dotenv()

teste = os.getenv('MICROSOFT_CLIENT_ID','pablo')
print(teste)