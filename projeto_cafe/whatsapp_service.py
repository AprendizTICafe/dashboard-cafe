import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class ZAPIService:
    """
    Serviço para enviar mensagens via Z-API (WhatsApp)
    """
    
    def __init__(self):
        self.instance_id = settings.ZAPI_INSTANCE_ID
        self.instance_token = settings.ZAPI_INSTANCE_TOKEN 
        self.client_token = settings.ZAPI_CLIENT_TOKEN
        
        # 👈 A URL oficial da Z-API exige o Token da Instância na rota
        self.base_url = f"https://api.z-api.io/instances/{self.instance_id}/token/{self.instance_token}"
        
        self.headers = {
            "Content-Type": "application/json",
            "Client-Token": self.client_token, # O Token do Cliente vai no header
        }
    
    def send_message(self, phone: str, message: str) -> bool:
        """
        Envia uma mensagem de texto via WhatsApp
        
        Args:
            phone: Número do telefone com código de país (ex: 5511999999999)
            message: Texto da mensagem (máximo 4096 caracteres)
        
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        if not phone or not message:
            logger.warning(f"Parâmetros inválidos: phone={phone}, message={message}")
            return False
        
        # Valida formato do telefone
        if not phone.startswith("55"):
            logger.warning(f"Telefone deve incluir código de país: {phone}")
            return False
        
        try:
            # 👈 O endpoint correto para envio de texto na Z-API é /send-text
            url = f"{self.base_url}/send-text"
            payload = {
                "phone": phone,
                "message": message,
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Mensagem enviada com sucesso para {phone}")
                return True
            else:
                logger.error(f"Erro ao enviar mensagem para {phone}: {response.status_code} - {response.text}")
                return False
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de conexão ao enviar para {phone}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Erro geral ao enviar mensagem: {str(e)}")
            return False
    
    def send_bulk_message(self, phones: list, message: str) -> dict:
        """
        Envia uma mensagem para múltiplos contatos
        """
        results = {"success": [], "failed": []}
        
        for phone in phones:
            if self.send_message(phone, message):
                results["success"].append(phone)
            else:
                results["failed"].append(phone)
        
        return results

def get_zapi_service():
    """Factory para obter instância do serviço Z-API"""
    return ZAPIService()