class NotificacaoAdvertencia:
    """
    Classe responsável por padronizar as mensagens enviadas via WhatsApp.
    Garante um layout limpo, informativo e estiloso para a equipe de TI e Gestores.
    """

    @staticmethod
    def _base_msg(titulo, colaborador, adv_id, status, extra=""):
        msg = (
            f"{titulo}\n\n"
            f"👤 *Colaborador:* {colaborador}\n"
            f"🆔 *ID da Advertência:* {adv_id}\n"
            f"📊 *Status:* {status}\n"
        )
        if extra:
            msg += f"\n{extra}"
        return msg

    @staticmethod
    def mensagem_criacao(colaborador, adv_id):
        return NotificacaoAdvertencia._base_msg(
            "🆕 *Nova Advertência Solicitada*", 
            colaborador, adv_id, "Solicitação Criada",
            "ℹ️ _Uma nova advertência foi registrada no sistema e aguarda envio ao RH._"
        )

    @staticmethod
    def mensagem_em_analise_rh(colaborador, adv_id):
        return NotificacaoAdvertencia._base_msg(
            "🔎 *Advertência em Análise (RH)*", 
            colaborador, adv_id, "Em Análise pelo RH",
            "ℹ️ _O departamento de RH recebeu e está revisando os detalhes da solicitação._"
        )

    @staticmethod
    def mensagem_enviada_diretoria(colaborador, adv_id):
        return NotificacaoAdvertencia._base_msg(
            "👔 *Enviada para Diretoria*", 
            colaborador, adv_id, "Em Análise (Diretoria)",
            "ℹ️ _A solicitação foi encaminhada para aprovação final da Diretoria._"
        )

    @staticmethod
    def mensagem_diretoria_aprovada(colaborador, adv_id):
        return NotificacaoAdvertencia._base_msg(
            "✅ *Advertência Aprovada*", 
            colaborador, adv_id, "Aprovada",
            "ℹ️ _A Diretoria aprovou a advertência! O processo retornou ao RH para agendamento._"
        )

    @staticmethod
    def mensagem_em_sindicancia_rh(colaborador, adv_id):
        return NotificacaoAdvertencia._base_msg(
            "⚠️ *Advertência em Sindicância*", 
            colaborador, adv_id, "Em Sindicância",
            "ℹ️ _A Diretoria solicitou sindicância. O RH precisará documentar mais evidências._"
        )

    @staticmethod
    def mensagem_sindicancia_reenviada(colaborador, adv_id):
        return NotificacaoAdvertencia._base_msg(
            "🔄 *Sindicância Reenviada*", 
            colaborador, adv_id, "Reanálise da Diretoria",
            "ℹ️ _O RH anexou a documentação de sindicância e devolveu para reavaliação da Diretoria._"
        )

    @staticmethod
    def mensagem_advertencia_agendada(colaborador, adv_id, data):
        return NotificacaoAdvertencia._base_msg(
            "📅 *Advertência Concluída / Agendada*", 
            colaborador, adv_id, "Concluída",
            f"📆 *Data de Aplicação:* {data}\n"
            "ℹ️ _O processo foi finalizado e a advertência está agendada para aplicação._"
        )