from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from django.http import FileResponse
from RH.models import Warnings, WarningWorkflow, GestorRH, WarningAttachments
from comum.constants import WARNING_STAGES, WORKFLOW_STAGES
from comum.validators import validate_user_email
from .models import GestorDiretoria
from RH.pdf_utils import gerar_pdf_advertencia
import logging

logger = logging.getLogger(__name__)


# --- VIEW DO PORTAL (EXIBE AS ESTATÍSTICAS) ---
@login_required
def advertencia(request):
    """
    Portal da Diretoria com estatísticas de advertências.
    A Diretoria visualiza todas as advertências em analise_diretoria
    """
    from django.db.models import Count, Q
    
    stats = Warnings.objects.filter(Active=True).aggregate(
        analise_diretoria=Count('id', filter=Q(CurrentStage=WARNING_STAGES['ANALISE_DIRETORIA'])),
        aprovadas=Count('id', filter=Q(CurrentStage=WARNING_STAGES['APROVADA'])),
        sindicancia=Count('id', filter=Q(CurrentStage=WARNING_STAGES['SINDICANCIA'])),
        concluidas=Count('id', filter=Q(CurrentStage=WARNING_STAGES['CONCLUIDA'])),
    )
    
    context = {
        'advertencias_em_analise_diretoria': stats['analise_diretoria'],
        'advertencias_aprovadas': stats['aprovadas'],
        'advertencias_em_sindicancia': stats['sindicancia'],
        'advertencias_concluidas': stats['concluidas'],
        
        'ultimas_advertencias': Warnings.objects.filter(
            Active=True, 
            CurrentStage=WARNING_STAGES['ANALISE_DIRETORIA']
        ).select_related('ColaboradorID').order_by('-CreatedAt')[:10],
    }
    return render(request, 'Diretoria/advertencia.html', context)


# --- VIEW DE VISUALIZACIÓN DE DETALHES (DIRETORIA) ---
@login_required
def view_advertencia_diretoria(request, id):
    """
    Exibe os detalhes de uma advertência em análise da Diretoria.
    A Diretoria pode visualizar todos os detalhes e aprovar ou enviar para sindicância.
    """
    advertencia = get_object_or_404(Warnings, pk=id, Active=True, CurrentStage=WARNING_STAGES['ANALISE_DIRETORIA'])
    
    # Importa os anexos e workflow
    anexos = WarningAttachments.objects.filter(AdvertenciaID=advertencia)
    workflow = WarningWorkflow.objects.filter(AdvertenciaID=advertencia).order_by('-CreatedAt')
    
    context = {
        'advertencia': advertencia,
        'anexos': anexos,
        'workflow': workflow,
    }
    return render(request, 'Diretoria/detalhes_advertencia_diretoria.html', context)


# --- VIEW DE APROVAÇÃO ---
@login_required
def approve_advertencia(request, id):
    """
    Aprova uma advertência.
    Muda o status de analise_diretoria para aprovada.
    """
    advertencia = get_object_or_404(Warnings, pk=id, Active=True, CurrentStage=WARNING_STAGES['ANALISE_DIRETORIA'])
    
    try:
        # Validar email do usuário
        is_valid, error_msg = validate_user_email(request.user)
        if not is_valid:
            messages.error(request, error_msg)
            return redirect('diretoria:view_advertencia_diretoria', id=id)
        
        # Buscar o GestorRH para registrar no workflow (não GestorDiretoria!)
        usuario_atual = GestorRH.objects.filter(Email=request.user.email).first()
        if not usuario_atual:
            logger.warning(f"GestorRH não encontrado para email {request.user.email}")
            messages.error(request, "Erro: Usuário RH não registrado no sistema.")
            return redirect('diretoria:view_advertencia_diretoria', id=id)
        
        with transaction.atomic():
            # Atualiza o status da advertência
            advertencia.CurrentStage = WARNING_STAGES['APROVADA']
            advertencia.UpdatedAt = timezone.now()
            advertencia.save()
            
            # Registra a ação no workflow com GestorRH (não GestorDiretoria)
            WarningWorkflow.objects.create(
                AdvertenciaID=advertencia,
                GestorRH=usuario_atual,
                Stage=WORKFLOW_STAGES['DIRETORIA_APROVA'],
                Comments='Advertência aprovada pela Diretoria.'
            )
        
        logger.info(f"Advertência {id} aprovada pela Diretoria por {request.user.email}")
        messages.success(request, "Advertência aprovada com sucesso!")
        return redirect('diretoria:advertencia')
    
    except Exception as e:
        logger.error(f"Erro ao aprovar advertência {id}: {str(e)}")
        messages.error(request, f"Erro ao aprovar advertência: {str(e)}")
        return redirect('diretoria:view_advertencia_diretoria', id=id)


# --- VIEW DE DEVOLUÇÃO PARA SINDICÂNCIA ---
@login_required
def return_to_investigation(request, id):
    """
    Devolve a advertência para o RH em status sindicancia.
    Muda o status de analise_diretoria para sindicancia.
    """
    if not request.method == 'POST':
        return redirect('diretoria:view_advertencia_diretoria', id=id)
    
    advertencia = get_object_or_404(Warnings, pk=id, Active=True, CurrentStage=WARNING_STAGES['ANALISE_DIRETORIA'])
    motivo_devolucao = request.POST.get('motivo_devolucao', '').strip()
    
    if not motivo_devolucao:
        messages.error(request, "Por favor, forneça um motivo para a devolução.")
        return redirect('diretoria:view_advertencia_diretoria', id=id)
    
    try:
        # Validar email do usuário
        is_valid, error_msg = validate_user_email(request.user)
        if not is_valid:
            messages.error(request, error_msg)
            return redirect('diretoria:view_advertencia_diretoria', id=id)
        
        # Buscar GestorRH, não GestorDiretoria
        usuario_atual = GestorRH.objects.filter(Email=request.user.email).first()
        if not usuario_atual:
            logger.warning(f"GestorRH não encontrado para email {request.user.email}")
            messages.error(request, "Erro: Usuário RH não registrado no sistema.")
            return redirect('diretoria:view_advertencia_diretoria', id=id)
        
        with transaction.atomic():
            # Atualiza o status para sindicância
            advertencia.CurrentStage = WARNING_STAGES['SINDICANCIA']
            advertencia.UpdatedAt = timezone.now()
            advertencia.save()
            
            # Registra a ação no workflow
            WarningWorkflow.objects.create(
                AdvertenciaID=advertencia,
                GestorRH=usuario_atual,
                Stage=WORKFLOW_STAGES['DIRETORIA_REPROVA'],
                Comments=f'Devolvida pela Diretoria para sindicância. Motivo: {motivo_devolucao}'
            )
        
        logger.info(f"Advertência {id} devolvida para sindicância por {request.user.email}")
        messages.success(request, "Advertência devolvida ao RH para sindicância!")
        return redirect('diretoria:advertencia')
    
    except Exception as e:
        logger.error(f"Erro ao devolver advertência {id}: {str(e)}")
        messages.error(request, f"Erro ao devolver advertência: {str(e)}")
        return redirect('diretoria:view_advertencia_diretoria', id=id)


# --- VIEW DE DOWNLOAD DE PDF ---
@login_required
def download_pdf_advertencia(request, id):
    """
    Gera e baixa um PDF da advertência para assinatura.
    """
    try:
        advertencia = get_object_or_404(Warnings, pk=id, Active=True)
        
        # Gera o PDF
        pdf_buffer = gerar_pdf_advertencia(advertencia)
        
        # Retorna o PDF como download
        response = FileResponse(pdf_buffer, as_attachment=True, filename=f'advertencia_{id}.pdf')
        response['Content-Type'] = 'application/pdf'
        return response
    
    except Exception as e:
        messages.error(request, f"Erro ao gerar PDF: {str(e)}")
        return redirect('diretoria:view_advertencia_diretoria', id=id)
