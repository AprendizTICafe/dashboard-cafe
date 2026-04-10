from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from RH.models import Warnings, GestorRH
from TI.models import GestorTI
from Diretoria.models import GestorDiretoria
from Contabilidade.models import GestorContabilidade
from Financeiro.models import GestorFinanceiro
from Logistica.models import GestorLogistica
from Manutencao.models import GestorManutencao
from Marketing.models import GestorMarketing
from SegurancaTrabalho.models import GestorSegurancaTrabalho
from .notificacoes import NotificacaoAdvertencia
from projeto_cafe.whatsapp_service import get_zapi_service
import logging

# Configuração de log para registrar sucessos e falhas
logger = logging.getLogger(__name__)

# --- FUNÇÕES AUXILIARES DE ENVIO (DISPARO DE WHATSAPP) ---

def _enviar_para_time_ti(mensagem):
    """Busca todos os gestores de TI ativos e envia a mensagem via Z-API."""
    try:
        gestores_ti = GestorTI.objects.filter(Active=True)
        if not gestores_ti.exists():
            return

        servico_zapi = get_zapi_service()
        for gestor in gestores_ti:
            if gestor.PhoneNumber:
                servico_zapi.send_message(gestor.PhoneNumber, mensagem)
    except Exception as e:
        logger.error(f"Falha ao enviar WhatsApp para o TI: {str(e)}")

def _enviar_para_time_rh(mensagem):
    """Busca todos os gestores de RH ativos e envia a mensagem via Z-API."""
    try:
        gestores_rh = GestorRH.objects.filter(Active=True)
        if not gestores_rh.exists():
            return

        servico_zapi = get_zapi_service()
        for gestor in gestores_rh:
            if gestor.PhoneNumber:
                servico_zapi.send_message(gestor.PhoneNumber, mensagem)
    except Exception as e:
        logger.error(f"Falha ao enviar WhatsApp para o RH: {str(e)}")

def _enviar_para_time_diretoria(mensagem):
    """Busca todos os gestores da Diretoria ativos e envia a mensagem via Z-API."""
    try:
        gestores_dir = GestorDiretoria.objects.filter(Active=True)
        if not gestores_dir.exists():
            return

        servico_zapi = get_zapi_service()
        for gestor in gestores_dir:
            if gestor.PhoneNumber:
                servico_zapi.send_message(gestor.PhoneNumber, mensagem)
    except Exception as e:
        logger.error(f"Falha ao enviar WhatsApp para a Diretoria: {str(e)}")

def _enviar_para_time_contabilidade(mensagem):
    """Busca todos os gestores de Contabilidade ativos e envia a mensagem via Z-API."""
    try:
        gestores = GestorContabilidade.objects.filter(Active=True)
        if not gestores.exists():
            return

        servico_zapi = get_zapi_service()
        for gestor in gestores:
            if gestor.PhoneNumber:
                servico_zapi.send_message(gestor.PhoneNumber, mensagem)
    except Exception as e:
        logger.error(f"Falha ao enviar WhatsApp para Contabilidade: {str(e)}")

def _enviar_para_time_financeiro(mensagem):
    """Busca todos os gestores de Financeiro ativos e envia a mensagem via Z-API."""
    try:
        gestores = GestorFinanceiro.objects.filter(Active=True)
        if not gestores.exists():
            return

        servico_zapi = get_zapi_service()
        for gestor in gestores:
            if gestor.PhoneNumber:
                servico_zapi.send_message(gestor.PhoneNumber, mensagem)
    except Exception as e:
        logger.error(f"Falha ao enviar WhatsApp para Financeiro: {str(e)}")

def _enviar_para_time_logistica(mensagem):
    """Busca todos os gestores de Logística ativos e envia a mensagem via Z-API."""
    try:
        gestores = GestorLogistica.objects.filter(Active=True)
        if not gestores.exists():
            return

        servico_zapi = get_zapi_service()
        for gestor in gestores:
            if gestor.PhoneNumber:
                servico_zapi.send_message(gestor.PhoneNumber, mensagem)
    except Exception as e:
        logger.error(f"Falha ao enviar WhatsApp para Logística: {str(e)}")

def _enviar_para_time_manutencao(mensagem):
    """Busca todos os gestores de Manutenção ativos e envia a mensagem via Z-API."""
    try:
        gestores = GestorManutencao.objects.filter(Active=True)
        if not gestores.exists():
            return

        servico_zapi = get_zapi_service()
        for gestor in gestores:
            if gestor.PhoneNumber:
                servico_zapi.send_message(gestor.PhoneNumber, mensagem)
    except Exception as e:
        logger.error(f"Falha ao enviar WhatsApp para Manutenção: {str(e)}")

def _enviar_para_time_marketing(mensagem):
    """Busca todos os gestores de Marketing ativos e envia a mensagem via Z-API."""
    try:
        gestores = GestorMarketing.objects.filter(Active=True)
        if not gestores.exists():
            return

        servico_zapi = get_zapi_service()
        for gestor in gestores:
            if gestor.PhoneNumber:
                servico_zapi.send_message(gestor.PhoneNumber, mensagem)
    except Exception as e:
        logger.error(f"Falha ao enviar WhatsApp para Marketing: {str(e)}")

def _enviar_para_time_seguranca_trabalho(mensagem):
    """Busca todos os gestores de Segurança do Trabalho ativos e envia a mensagem via Z-API."""
    try:
        gestores = GestorSegurancaTrabalho.objects.filter(Active=True)
        if not gestores.exists():
            return

        servico_zapi = get_zapi_service()
        for gestor in gestores:
            if gestor.PhoneNumber:
                servico_zapi.send_message(gestor.PhoneNumber, mensagem)
    except Exception as e:
        logger.error(f"Falha ao enviar WhatsApp para Segurança do Trabalho: {str(e)}")

def _enviar_para_gestor_origem(advertencia, mensagem):
    """
    Identifica o gestor que criou a advertência baseando-se no e-mail 
    e no departamento de origem, enviando o status atual para ele.
    """
    if not advertencia.Gestor or not advertencia.Gestor.email:
        logger.warning(f"Advertência {advertencia.AdvertenciaID} sem e-mail de gestor.")
        return

    try:
        email_gestor = advertencia.Gestor.email
        telefone = None

        # Lógica de roteamento: busca o telefone na tabela correta conforme o departamento
        if advertencia.DepartmentOrigin == "Tecnologia da Informação":
            gestor_origem = GestorTI.objects.filter(Email=email_gestor, Active=True).first()
            if gestor_origem: telefone = gestor_origem.PhoneNumber
            
        elif advertencia.DepartmentOrigin == "Recursos Humanos":
            gestor_origem = GestorRH.objects.filter(Email=email_gestor, Active=True).first()
            if gestor_origem: telefone = gestor_origem.PhoneNumber
            
        elif advertencia.DepartmentOrigin == "Diretoria":
            gestor_origem = GestorDiretoria.objects.filter(Email=email_gestor, Active=True).first()
            if gestor_origem: telefone = gestor_origem.PhoneNumber

        elif advertencia.DepartmentOrigin == "Contabilidade":
            gestor_origem = GestorContabilidade.objects.filter(Email=email_gestor, Active=True).first()
            if gestor_origem: telefone = gestor_origem.PhoneNumber

        elif advertencia.DepartmentOrigin == "Financeiro":
            gestor_origem = GestorFinanceiro.objects.filter(Email=email_gestor, Active=True).first()
            if gestor_origem: telefone = gestor_origem.PhoneNumber

        elif advertencia.DepartmentOrigin == "Logística":
            gestor_origem = GestorLogistica.objects.filter(Email=email_gestor, Active=True).first()
            if gestor_origem: telefone = gestor_origem.PhoneNumber

        elif advertencia.DepartmentOrigin == "Manutenção":
            gestor_origem = GestorManutencao.objects.filter(Email=email_gestor, Active=True).first()
            if gestor_origem: telefone = gestor_origem.PhoneNumber

        elif advertencia.DepartmentOrigin == "Marketing":
            gestor_origem = GestorMarketing.objects.filter(Email=email_gestor, Active=True).first()
            if gestor_origem: telefone = gestor_origem.PhoneNumber

        elif advertencia.DepartmentOrigin == "Segurança do Trabalho":
            gestor_origem = GestorSegurancaTrabalho.objects.filter(Email=email_gestor, Active=True).first()
            if gestor_origem: telefone = gestor_origem.PhoneNumber

        if telefone:
            servico_zapi = get_zapi_service()
            servico_zapi.send_message(telefone, mensagem)
            logger.info(f"Notificação enviada para origem: {email_gestor}")
        else:
            logger.warning(f"Gestor de origem ativo não encontrado para o e-mail {email_gestor}")

    except Exception as e:
        logger.error(f"Falha ao notificar gestor de origem {advertencia.AdvertenciaID}: {str(e)}")


# --- SIGNALS (GATILHOS DO SISTEMA) ---

@receiver(pre_save, sender=Warnings)
def cache_previous_stage(sender, instance, **kwargs):
    """
    Antes de salvar, verifica qual era o estágio anterior da advertência 
    e armazena temporariamente na instância.
    """
    if instance.pk:  # Se o objeto já existe (é uma edição)
        try:
            old_instance = Warnings.objects.get(pk=instance.pk)
            instance._previous_stage = old_instance.CurrentStage
        except Warnings.DoesNotExist:
            instance._previous_stage = None
    else:  # Se for uma criação nova
        instance._previous_stage = None

@receiver(post_save, sender=Warnings)
def notificar_mudanca_advertencia(sender, instance, created, **kwargs):
    """
    Após salvar, decide se deve enviar notificações de criação ou de mudança de fase.
    """
    try:
        if created:
            # Caso seja um registro novo, notifica apenas o TI (estágio inicial)
            _notificar_criacao_ti(instance)
        else:
            # Caso seja edição, verifica se o estágio (CurrentStage) mudou
            stage_anterior = getattr(instance, '_previous_stage', None)
            if stage_anterior and stage_anterior != instance.CurrentStage:
                _rotear_notificacao_por_estagio(instance, stage_anterior)
    except Exception as e:
        logger.error(f"Erro no processamento do signal: {str(e)}")


# --- LÓGICA DE NEGÓCIO E ROTEAMENTO ---

def _notificar_criacao_ti(advertencia):
    """Prepara a mensagem inicial de criação para o time de TI."""
    colaborador = advertencia.ColaboradorID.Name if advertencia.ColaboradorID else "Desconhecido"
    mensagem = NotificacaoAdvertencia.mensagem_criacao(colaborador, advertencia.AdvertenciaID)
    _enviar_para_time_ti(mensagem)

def _rotear_notificacao_por_estagio(advertencia, stage_anterior):
    """
    Define quem deve ser notificado com base na transição de estágios.
    Utiliza o padrão de lista de chamadas (callbacks) para organizar os envios.
    """
    colaborador = advertencia.ColaboradorID.Name if advertencia.ColaboradorID else "Desconhecido"
    stage_novo = advertencia.CurrentStage
    adv_id = advertencia.AdvertenciaID
    mensagem = None
    calls_to_make = []

    # 1. Transição: Criada -> Análise RH
    if stage_anterior == 'criada' and stage_novo == 'analise_rh':
        mensagem = NotificacaoAdvertencia.mensagem_em_analise_rh(colaborador, adv_id)
        calls_to_make.append(lambda: _enviar_para_time_rh(mensagem))
    
    # 2. Transição: Análise RH -> Análise Diretoria
    elif stage_anterior == 'analise_rh' and stage_novo == 'analise_diretoria':
        mensagem = NotificacaoAdvertencia.mensagem_enviada_diretoria(colaborador, adv_id)
        calls_to_make.append(lambda: _enviar_para_time_diretoria(mensagem))
        calls_to_make.append(lambda: _enviar_para_time_rh(mensagem))
    
    # 3. Transição: Diretoria aprova a advertência
    elif stage_anterior == 'analise_diretoria' and stage_novo == 'aprovada':
        mensagem = NotificacaoAdvertencia.mensagem_diretoria_aprovada(colaborador, adv_id)
        calls_to_make.append(lambda: _enviar_para_time_rh(mensagem))
        calls_to_make.append(lambda: _enviar_para_time_diretoria(mensagem))
    
    # 4. Transição: Diretoria solicita investigação adicional (Sindicância)
    elif stage_anterior == 'analise_diretoria' and stage_novo == 'em_sindicancia':
        mensagem = NotificacaoAdvertencia.mensagem_em_sindicancia_rh(colaborador, adv_id)
        calls_to_make.append(lambda: _enviar_para_time_rh(mensagem))
        calls_to_make.append(lambda: _enviar_para_time_diretoria(mensagem))
    
    # 5. Transição: Retorno da Sindicância para a Diretoria
    elif stage_anterior == 'em_sindicancia' and stage_novo == 'analise_diretoria':
        mensagem = NotificacaoAdvertencia.mensagem_sindicancia_reenviada(colaborador, adv_id)
        calls_to_make.append(lambda: _enviar_para_time_diretoria(mensagem))
    
    # 6. Transição: Aprovada -> Concluída (Agendamento da aplicação)
    elif stage_anterior == 'aprovada' and stage_novo == 'concluida':
        data_agendada = getattr(advertencia, 'SchenduledDate', None)
        data = data_agendada.strftime("%d/%m/%Y") if data_agendada else "A definir"
        mensagem = NotificacaoAdvertencia.mensagem_advertencia_agendada(colaborador, adv_id, data)
        calls_to_make.append(lambda: _enviar_para_time_rh(mensagem))

    # Se uma mensagem de transição foi definida, notifica também o gestor que abriu o processo
    if mensagem:
        calls_to_make.append(lambda: _enviar_para_gestor_origem(advertencia, mensagem))

    # Executa todos os disparos agendados na lista
    if calls_to_make:
        for call in calls_to_make:
            call()