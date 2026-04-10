"""
Funções utilitárias para validações comuns no sistema.
"""
import logging
from django.http import JsonResponse
from datetime import datetime, timedelta
from comum.constants import WARNING_STAGES, VALID_TRANSITIONS

logger = logging.getLogger(__name__)


def validate_user_email(user):
    """
    Valida se o usuário tem email cadastrado.
    
    Args:
        user: Objeto User do Django
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not user or not user.email:
        logger.warning(f"Tentativa de operação sem email válido. User: {user}")
        return False, "Usuário não possui email cadastrado no sistema."
    
    return True, None


def validate_date_schedule(date_str, min_days=1, max_days=30):
    """
    Valida se uma data de agendamento é válida.
    
    Args:
        date_str: String de data (formato YYYY-MM-DD)
        min_days: Número mínimo de dias no futuro (padrão: 1)
        max_days: Número máximo de dias no futuro (padrão: 30)
        
    Returns:
        tuple: (is_valid, error_message, parsed_date)
    """
    try:
        scheduled_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return False, "Formato de data inválido. Use YYYY-MM-DD.", None
    
    today = datetime.now().date()
    days_difference = (scheduled_date - today).days
    
    if days_difference < min_days:
        return False, f"Data deve ser no mínimo {min_days} dia(s) no futuro.", None
    
    if days_difference > max_days:
        return False, f"Data não pode ser superior a {max_days} dias no futuro.", None
    
    return True, None, scheduled_date


def validate_file_upload(uploaded_file, allowed_extensions=None):
    """
    Valida arquivo enviado.
    
    Args:
        uploaded_file: Arquivo enviado (request.FILES)
        allowed_extensions: Lista de extensões permitidas (ex: ['pdf', 'doc', 'docx'])
        
    Returns:
        tuple: (is_valid, error_message, file_type)
    """
    if not uploaded_file:
        return False, "Nenhum arquivo foi enviado.", None
    
    if not uploaded_file.content_type:
        return False, "Arquivo sem tipo de conteúdo válido.", None
    
    if '/' not in uploaded_file.content_type:
        return False, "Tipo de arquivo inválido.", None
    
    file_type = uploaded_file.content_type.split('/')[-1]
    
    if allowed_extensions and file_type not in allowed_extensions:
        return False, f"Tipo de arquivo não permitido. Extensões aceitas: {', '.join(allowed_extensions)}", None
    
    return True, None, file_type


def validate_state_transition(current_stage, next_stage):
    """
    Valida se a transição entre estágios é permitida.
    
    Args:
        current_stage: Estágio atual da advertência
        next_stage: Próximo estágio desejado
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if current_stage not in VALID_TRANSITIONS:
        return False, f"Estágio '{current_stage}' não reconhecido no sistema."
    
    allowed_transitions = VALID_TRANSITIONS[current_stage]
    
    if next_stage not in allowed_transitions:
        return False, f"Transição de '{current_stage}' para '{next_stage}' não é permitida. Estágios válidos: {', '.join(allowed_transitions)}"
    
    return True, None


def error_response(message, status_code=400):
    """
    Retorna resposta de erro em JSON.
    
    Args:
        message: Mensagem de erro
        status_code: Código HTTP
        
    Returns:
        JsonResponse
    """
    logger.error(f"Erro retornado ao usuário: {message}")
    return JsonResponse({'error': message}, status=status_code)


def success_response(message, data=None, status_code=200):
    """
    Retorna resposta de sucesso em JSON.
    
    Args:
        message: Mensagem de sucesso
        data: Dados adicionais para retornar
        status_code: Código HTTP
        
    Returns:
        JsonResponse
    """
    response = {'success': message}
    if data:
        response['data'] = data
    
    logger.info(f"Sucesso: {message}")
    return JsonResponse(response, status=status_code)
