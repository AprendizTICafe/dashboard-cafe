from django.shortcuts import render, redirect, get_object_or_404
from RH.models import WarningAttachments, Warnings, WarningWorkflow, GestorRH
from comum.models import Colaborador
from comum.constants import WARNING_STAGES, WORKFLOW_STAGES, DEPARTMENTS
from comum.validators import validate_user_email, validate_file_upload
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q
import logging

logger = logging.getLogger(__name__)

# --- VIEW DO PORTAL (EXIBE AS ESTATÍSTICAS) ---
@login_required
def advertencia(request):
    """
    Esta view calcula as contagens para os cards.
    Toda vez que o usuário é redirecionado para cá após um POST,
    os counts são refeitos, atualizando o número na tela.
    """
    # Usa agregação em uma única query ao invés de múltiplas queries de COUNT
    stats = Warnings.objects.filter(
        DepartmentOrigin=DEPARTMENTS['TI'],
        Active=True
    ).aggregate(
        solicitadas=Count('id', filter=Q(CurrentStage=WARNING_STAGES['SOLICITADA'])),
        analise_rh=Count('id', filter=Q(CurrentStage=WARNING_STAGES['ANALISE_RH'])),
        analise_diretoria=Count('id', filter=Q(CurrentStage=WARNING_STAGES['ANALISE_DIRETORIA'])),
        aprovadas=Count('id', filter=Q(CurrentStage=WARNING_STAGES['APROVADA'])),
        concluidas=Count('id', filter=Q(CurrentStage=WARNING_STAGES['CONCLUIDA'])),
    )

    context = {
        'advertencias_solicitadas': stats['solicitadas'],
        'advertencias_em_analise_rh': stats['analise_rh'],
        'advertencias_em_analise_diretoria': stats['analise_diretoria'],
        'advertencias_aprovadas': stats['aprovadas'],
        'advertencias_concluidas': stats['concluidas'],
        
        'ultimas_advertencias': Warnings.objects.filter(
            DepartmentOrigin=DEPARTMENTS['TI'],
            Active=True
        ).select_related('ColaboradorID').order_by('-CreatedAt')[:10],
        
        'colaboradores': Colaborador.objects.filter(Active=True).order_by('Name'),
    }
    return render(request, 'TI/advertencia.html', context)


# --- VIEW DE CRIAÇÃO DA ADVERTÊNCIA ---
@login_required
def nova_advertencia(request):
    """
    Processa o formulário de envio. Garante que o solicitante (Users)
    exista e esteja vinculado ao usuário logado (auth.User).
    """
    if request.method == "POST":
        usuario = request.user
        
        colaborador = get_object_or_404(Colaborador, ColaboradorID=request.POST.get('colaborador'))
        data_ocorrencia = request.POST.get('data_ocorrencia', '').strip()
        descricao = request.POST.get('Descricao', '').strip()

        try:
            # Validar email do usuário
            is_valid, error_msg = validate_user_email(usuario)
            if not is_valid:
                messages.error(request, error_msg)
                return redirect('ti:advertencia')
            
            if not data_ocorrencia or not descricao:
                messages.error(request, "Data e descrição são obrigatórias.")
                return redirect('ti:advertencia')
            
            # Iniciamos uma transação atômica: ou salva tudo (adv + anexos + workflow) ou nada
            with transaction.atomic():
                
                # Criação do registro principal de Advertência
                nova_war = Warnings.objects.create(
                    ColaboradorID=colaborador,
                    DepartmentOrigin=DEPARTMENTS['TI'],
                    Gestor=usuario,  
                    IncidentDate=data_ocorrencia,
                    Description=descricao,
                    CurrentStage=WARNING_STAGES['SOLICITADA']
                )

                # Processamento de múltiplos arquivos anexos
                arquivos = request.FILES.getlist('arquivos')
                for f in arquivos:
                    # Validar arquivo
                    is_valid, error_msg, file_type = validate_file_upload(f)
                    if not is_valid:
                        logger.warning(f"Arquivo inválido: {f.name} - {error_msg}")
                        continue
                    
                    if f.size <= 10 * 1024 * 1024:  # 10MB limit
                        WarningAttachments.objects.create(
                            AdvertenciaID=nova_war,
                            FileName=f.name,
                            FileType=file_type,
                            FilePath=f
                        )
                    else:
                        logger.warning(f"Arquivo {f.name} ultrapassa 10MB")
                        messages.warning(request, f"Arquivo {f.name} é muito grande (máximo 10MB)")

                # Registro do primeiro passo no histórico (Workflow)
                WarningWorkflow.objects.create(
                    AdvertenciaID=nova_war,
                    Stage=WORKFLOW_STAGES['CRIADA'],
                    Comments="Solicitação de advertência criada."
                )

            # Se chegou aqui, deu tudo certo
            logger.info(f"Advertência criada por {usuario.email} para {colaborador.Name}")
            messages.success(request, "Solicitação de advertência criada com sucesso!")
            return redirect('ti:advertencia')  # Redireciona para atualizar as estatísticas

        except Exception as e:
            # Em caso de erro, exibe a mensagem e volta ao portal
            messages.error(request, f"Erro ao processar solicitação: {e}")
            return redirect('ti:advertencia')

    # --- Lógica para GET (Exibir formulário) ---
    # Filtramos diretamente pelo departamento de TI e colaboradores ativos
    # Isso garante que a lista apareça mesmo se o Gestor não tiver cadastro na tabela TI.models.Gestor ainda
    colaboradores = Colaborador.objects.filter(Department="Tecnologia da Informação", Active=True)

    return render(request, 'TI/nova_advertencia.html', {'colaboradores': colaboradores.order_by('Name')})

def advertencia_list(request):
    # 1. Filtra por departamento de TI (para o app TI)
    # Lista de colaboradores para o <select> do filtro
    colaboradores_dept = Colaborador.objects.filter(Department="Tecnologia da Informação", Active=True).order_by('Name')
    queryset = Warnings.objects.filter(DepartmentOrigin="Tecnologia da Informação")

    # 2. Captura os filtros
    ColaboradorID = request.GET.get('colaborador')
    CurrentStage = request.GET.get('status')
    CreatedAt = request.GET.get('data_inicio')

    # 3. Aplica os filtros
    if ColaboradorID:
        # Filtramos pelo ID do colaborador selecionado
        queryset = queryset.filter(ColaboradorID__ColaboradorID=ColaboradorID)
    
    if CurrentStage:
        queryset = queryset.filter(CurrentStage=CurrentStage)
        
    if CreatedAt:
        queryset = queryset.filter(CreatedAt__gte=CreatedAt)

    # 4. Mensagem de erro caso não encontre nada
    if not queryset.exists() and (ColaboradorID or CurrentStage or CreatedAt):
        messages.error(request, "Nenhuma advertência encontrada para os filtros aplicados.")

    context = {
        'advertencias': queryset,
        'colaboradores_list': colaboradores_dept, # Enviamos a lista para o select
        'filtros': request.GET
    }
    return render(request, 'TI/advertencia.html', context)


# --- VIEW DE VISUALIZACIÓN DE DETALHES ---
@login_required
def view_advertencia(request, id):
    """
    Exibe os detalhes de uma advertência criada por TI.
    Apenas o criador da advertência pode enviá-la para o RH.
    """
    advertencia = get_object_or_404(Warnings, pk=id, Active=True)
    anexos = WarningAttachments.objects.filter(AdvertenciaID=advertencia)
    workflow = WarningWorkflow.objects.filter(AdvertenciaID=advertencia).order_by('-CreatedAt')
    
    # Verifica se o usuário logado é o criador da advertência
    email_usuario = request.user.email
    pode_enviar = (advertencia.Gestor and advertencia.Gestor.email == email_usuario and 
                  advertencia.CurrentStage == 'solicitada')
    
    context = {
        'advertencia': advertencia,
        'anexos': anexos,
        'workflow': workflow,
        'pode_enviar': pode_enviar,
    }
    return render(request, 'TI/detalhes_advertencia.html', context)


# --- VIEW DE ENVIO PARA RH ---
@login_required
def send_to_rh(request, id):
    """
    Envia a advertência do TI para análise do RH.
    Muda o status de "criada" para "analise_rh".
    """
    advertencia = get_object_or_404(Warnings, pk=id, Active=True)
    
    # Verifica se o usuário logado é o criador e se o status permite
    email_usuario = request.user.email
    if not email_usuario:
        messages.error(request, "Erro: Usuário sem email configurado.")
        return redirect('ti:advertencia')

    print(f"E-mail Logado: {email_usuario}")
    print(f"Status Atual: {advertencia.CurrentStage}")
    
    
    try:
        with transaction.atomic():
            # Atualiza o status da advertência
            advertencia.CurrentStage = 'analise_rh'
            advertencia.UpdatedAt = timezone.now()
            advertencia.save()
            
            # Registra a ação no workflow
            WarningWorkflow.objects.create(
                AdvertenciaID=advertencia,
                Stage='analise_rh',
                Comments='Advertência enviada para análise do RH.'
            )
        
        messages.success(request, "Advertência enviada com sucesso para o RH!")
        return redirect('ti:advertencia')
    
    except Exception as e:
        messages.error(request, f"Erro ao enviar advertência: {str(e)}")
        return redirect('ti:view_advertencia', id=id)


def excluir_advertencia(request, id):
    if request.method == 'POST':
        advertencia = get_object_or_404(Warnings, pk=id)
        
        # Apenas muda o status para invisível
        advertencia.Active = False
        advertencia.save()
        
        messages.success(request, "Advertência removida da visualização.")
            
    return redirect('ti:advertencia')
