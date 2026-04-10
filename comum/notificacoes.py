from projeto_cafe.whatsapp_service import get_zapi_service
import logging

logger = logging.getLogger(__name__)

def enviar_notificacao_whatsapp(telefone: str, mensagem: str):
    if not telefone or not mensagem:
        return None
    try:
        servico = get_zapi_service()
        return servico.send_message(telefone, mensagem)
    except Exception as e:
        logger.error(f"Erro ao enviar notificação via WhatsApp: {e}")
        raise

class NotificacaoAdvertencia:
    """Templates de mensagens de notificação de advertências"""

    @staticmethod
    def mensagem_em_analise_rh(colaborador_nome: str, advertencia_id: int):
        return (
            f"🟠 *Advertência em Análise pelo RH*\n\n"
            f"Colaborador: {colaborador_nome}\n"
            f"ID: #{advertencia_id}\n"
            f"Status: Em Análise RH\n\n"
            f"O RH iniciou a conferência desta solicitação."
        )

    @staticmethod
    def mensagem_enviada_diretoria(colaborador_nome: str, advertencia_id: int):
        return (
            f"📤 *Advertência Enviada à Diretoria*\n\n"
            f"Colaborador: {colaborador_nome}\n"
            f"ID: #{advertencia_id}\n"
            f"Status: 🔴 Análise Diretoria\n\n"
            f"A advertência foi enviada para decisão final."
        )

    @staticmethod
    def mensagem_diretoria_aprovada(colaborador_nome: str, advertencia_id: int):
        return (
            f"✅ *Advertência Aprovada*\n\n"
            f"Colaborador: {colaborador_nome}\n"
            f"ID: #{advertencia_id}\n"
            f"Status: ✅ Aprovada\n\n"
            f"A Diretoria aprovou o seguimento desta advertência."
        )

    @staticmethod
    def mensagem_em_sindicancia_rh(colaborador_nome: str, advertencia_id: int):
        return (
            f"⚠️ *Advertência em Sindicância*\n\n"
            f"Colaborador: {colaborador_nome}\n"
            f"ID: #{advertencia_id}\n"
            f"Status: ⚠️ Sindicância\n\n"
            f"A Diretoria solicitou a abertura de sindicância para este caso."
        )

    @staticmethod
    def mensagem_sindicancia_reenviada(colaborador_nome: str, advertencia_id: int):
        return (
            f"📤 *Sindicância Reenviada à Diretoria*\n\n"
            f"Colaborador: {colaborador_nome}\n"
            f"ID: #{advertencia_id}\n"
            f"Status: 🔴 Análise Diretoria\n\n"
            f"Documentação complementada e reenviada para a Diretoria."
        )

    @staticmethod
    def mensagem_advertencia_agendada(colaborador_nome: str, advertencia_id: int, data_agendamento: str):
        return (
            f"📅 *Advertência Agendada*\n\n"
            f"Colaborador: {colaborador_nome}\n"
            f"ID: #{advertencia_id}\n"
            f"Status: ✅ Concluída\n"
            f"Data de Aplicação: {data_agendamento}\n\n"
            f"A advertência foi finalizada e está pronta para aplicação."
        )