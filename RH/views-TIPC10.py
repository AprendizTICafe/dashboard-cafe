from django.shortcuts import render, redirect, get_object_or_404
from .models import Warnings, WarningWorkflow, GestorRH, WarningAttachments
from comum.models import Colaborador
from comum.constants import WARNING_STAGES, WORKFLOW_STAGES, VALID_TRANSITIONS
from comum.validators import validate_user_email, validate_date_schedule, validate_file_upload, validate_state_transition
from django.contrib import messages
from django.db import IntegrityError
from django.db import transaction
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.http import FileResponse
from .pdf_utils import gerar_pdf_advertencia
import logging

logger = logging.getLogger(__name__)


# --- VIEW DE CADASTRO DE NOVOS COLABORADORES (FUNCIONÁRIOS) ---
@login_required
def cadastro_colaborador(request):
    """
    Recebe os dados do formulário de novos funcionários.
    Após o cadastro, redireciona para o portal para que o novo 
    colaborador já apareça na lista de seleção de advertências.
    """
    if request.method == "POST":
        # Coletando e limpando os dados (removendo espaços extras com strip)
        nome = request.POST.get('Name', '').strip()
        email = request.POST.get('Email', '').strip()
        telefone = request.POST.get('PhoneNumber', '').strip()
        cargo = request.POST.get('Position', '').strip()
        departamento_escolhido = request.POST.get('Department', '').strip()

        if not nome:
            messages.error(request, "Nome obrigatório!")
            return redirect('rh:cadastro_colaborador')

        try:
            Colaborador.objects.create(
                Name=nome,
                Email=email,
                PhoneNumber=telefone,
                Position=cargo,
                Department=departamento_escolhido
            )
            messages.success(request, f"Colaborador '{nome}' cadastrado com sucesso!")
            return redirect('rh:advertencia')
        except IntegrityError:
            messages.error(request, f"Erro ao cadastrar: o e-mail '{email}' já está em uso.")
            return redirect('rh:cadastro_colaborador')

    # Se o método for GET, apenas renderiza a página do formulário
    grupos = Group.objects.all().order_by('name')
    return render(request, 'RH/cadastro_colaborador.html', {'grupos': grupos})


# --- VIEW DO PORTAL (EXIBE AS ESTATÍSTICAS) ---
@login_required
def advertencia(request):
    """
    Esta view calcula as contagens para os cards.
    Toda vez que o usuário é redirecionado para cá após um POST,
    os counts são refeitos, atualizando o número na tela.
    """
    from django.db.models import Count, Q
    
    # Usa agregação em uma única query ao invés de múltiplas queries de COUNT
    stats = Warnings.objects.filter(Active=True).aggregate(
        analise_rh=Count('id', filter=Q(CurrentStage=WARNING_STAGES['ANALISE_RH'])),
        analise_diretoria=Count('id', filter=Q(CurrentStage=WARNING_STAGES['ANALISE_DIRETORIA'])),
        aprovadas=Count('id', filter=Q(CurrentStage=WARNING_STAGES['APROVADA'])),
        sindicancia=Count('id', filter=Q(CurrentStage=WARNING_STAGES['SINDICANCIA'])),
        concluidas=Count('id', filter=Q(CurrentStage=WARNING_STAGES['CONCLUIDA'])),
    )

    context = {
        'advertencias_em_analise_rh': stats['analise_rh'],
        'advertencias_em_analise_diretoria': stats['analise_diretoria'],
        'advertencias_aprovadas': stats['aprovadas'],
        'advertencias_em_sindicancia': stats['sindicancia'],
        'advertencias_concluidas': stats['concluidas'],
        
        # Usa select_related para otimizar query de colaborador
        'ultimas_advertencias': Warnings.objects.filter(
            Active=True, 
            CurrentStage__in=[
                WARNING_STAGES['ANALISE_RH'],
                WARNING_STAGES['ANALISE_DIRETORIA'],
                WARNING_STAGES['CONCLUIDA'],
                WARNING_STAGES['APROVADA'],
                WARNING_STAGES['SINDICANCIA']
            ]
        ).select_related('ColaboradorID').order_by('-CreatedAt')[:10],
        
        # Necessário para popular o select do formulário dentro do portal
        'colaboradores': Colaborador.objects.filter(Active=True).order_by('Name'),
    }
    return render(request, 'RH/advertencia.html', context)


# --- VIEW DE VISUALIZAÇÃO DE DETALHES (RH) ---
@login_required
def view_advertencia_rh(request, id):
    """
    Exibe os detalhes de uma advertência em análise do RH.
    O RH pode visualizar a descrição, editar o texto oficial e enviar para a Diretoria.
    Aceita os status: analise_rh, aprovada e sindicancia
    """
    advertencia = get_object_or_404(
        Warnings, 
        pk=id, 
        Active=True, 
        CurrentStage__in=[
            WARNING_STAGES['ANALISE_RH'],
            WARNING_STAGES['APROVADA'],
            WARNING_STAGES['SINDICANCIA']
        ]
    )
    anexos = WarningAttachments.objects.filter(AdvertenciaID=advertencia)
    workflow = WarningWorkflow.objects.filter(AdvertenciaID=advertencia).order_by('-CreatedAt')
    
    context = {
        'advertencia': advertencia,
        'anexos': anexos,
        'workflow': workflow,
    }
    return render(request, 'RH/detalhes_advertencia_rh.html', context)


# --- VIEW DE EDIÇÃO DO TEXTO OFICIAL ---
@login_required
def edit_advertencia(request, id):
    """
    Permite que o RH edite o texto oficial da advertência.
    Aceita o status: analise_rh
    """
    advertencia = get_object_or_404(Warnings, pk=id, Active=True, CurrentStage=WARNING_STAGES['ANALISE_RH'])
    
    if request.method == 'POST':
        novo_texto = request.POST.get('OfficialText', '').strip()
        
        if not novo_texto:
            messages.error(request, "O texto oficial não pode estar vazio.")
            return redirect('rh:view_advertencia_rh', id=id)
        
        try:
            # Validar email do usuário
            is_valid, error_msg = validate_user_email(request.user)
            if not is_valid:
                messages.error(request, error_msg)
                return redirect('rh:view_advertencia_rh', id=id)
            
            with transaction.atomic():
                # Atualiza o texto oficial
                advertencia.OfficialText = novo_texto
                advertencia.UpdatedAt = timezone.now()
                advertencia.save()
                
                # Registra a ação no workflow
                usuario_atual = GestorRH.objects.filter(Email=request.user.email).first()
                if not usuario_atual:
                    logger.warning(f"GestorRH não encontrado para email {request.user.email}")
                    messages.error(request, "Erro: Usuário RH não registrado no sistema.")
                    return redirect('rh:view_advertencia_rh', id=id)
                
                WarningWorkflow.objects.create(
                    AdvertenciaID=advertencia,
                    GestorRH=usuario_atual,
                    Stage=WORKFLOW_STAGES['REVISA_RH'],
                    Comments='Texto oficial editado pelo RH.'
                )
                
                logger.info(f"Texto oficial da advertência {id} atualizado por {request.user.email}")
                messages.success(request, "Texto oficial atualizado com sucesso!")
                return redirect('rh:view_advertencia_rh', id=id)
        
        except Exception as e:
            logger.error(f"Erro ao atualizar texto oficial de {id}: {str(e)}")
            messages.error(request, f"Erro ao atualizar texto oficial: {str(e)}")
            return redirect('rh:view_advertencia_rh', id=id)
    
    return redirect('rh:view_advertencia_rh', id=id)


# --- VIEW DE ENVIO PARA DIRETORIA ---
@login_required
def send_to_diretoria(request, id):
    """
    Envia a advertência do RH para análise da Diretoria.
    Muda o status de analise_rh para analise_diretoria.
    """
    advertencia = get_object_or_404(Warnings, pk=id, Active=True, CurrentStage=WARNING_STAGES['ANALISE_RH'])
    
    try:
        # Validar email do usuário
        is_valid, error_msg = validate_user_email(request.user)
        if not is_valid:
            messages.error(request, error_msg)
            return redirect('rh:view_advertencia_rh', id=id)
        
        usuario_atual = GestorRH.objects.filter(Email=request.user.email).first()
        if not usuario_atual:
            logger.warning(f"GestorRH não encontrado para email {request.user.email}")
            messages.error(request, "Erro: Usuário RH não registrado no sistema.")
            return redirect('rh:view_advertencia_rh', id=id)
        
        # Validar transição de estado
        is_valid, error_msg = validate_state_transition(
            advertencia.CurrentStage,
            WARNING_STAGES['ANALISE_DIRETORIA']
        )
        if not is_valid:
            messages.error(request, error_msg)
            return redirect('rh:view_advertencia_rh', id=id)
        
        with transaction.atomic():
            # Atualiza o status da advertência
            advertencia.CurrentStage = WARNING_STAGES['ANALISE_DIRETORIA']
            advertencia.UpdatedAt = timezone.now()
            advertencia.save()
            
            # Registra a ação no workflow
            WarningWorkflow.objects.create(
                AdvertenciaID=advertencia,
                GestorRH=usuario_atual,
                Stage=WORKFLOW_STAGES['ENVIA_DIRETORIA'],
                Comments='Advertência encaminhada para análise da Diretoria.'
            )
        
        logger.info(f"Advertência {id} encaminhada para Diretoria por {request.user.email}")
        messages.success(request, "Advertência encaminhada com sucesso para a Diretoria!")
        return redirect('rh:advertencia')
    
    except Exception as e:
        logger.error(f"Erro ao encaminhar advertência {id}: {str(e)}")
        messages.error(request, f"Erro ao encaminhar advertência: {str(e)}")
        return redirect('rh:view_advertencia_rh', id=id)


# --- VIEW DE SINDICÂNCIA/INVESTIGAÇÃO (OPCIONAL) ---
@login_required
def start_investigation(request, id):
    """
    Inicia/registra uma investigação (sindicância) sobre a advertência.
    Permite ao RH anexar documentos relacionados à investigação.
    Apenas disponível quando o status é aprovada.
    """
    advertencia = get_object_or_404(Warnings, pk=id, Active=True, CurrentStage=WARNING_STAGES['APROVADA'])
    
    if request.method == 'POST':
        descricao_investigacao = request.POST.get('descricao_investigacao', '').strip()
        
        if not descricao_investigacao:
            messages.error(request, "Por favor, forneça uma descrição para a investigação.")
            return redirect('rh:view_advertencia_rh', id=id)
        
        try:
            # Validar email do usuário
            is_valid, error_msg = validate_user_email(request.user)
            if not is_valid:
                messages.error(request, error_msg)
                return redirect('rh:view_advertencia_rh', id=id)
            
            usuario_atual = GestorRH.objects.filter(Email=request.user.email).first()
            if not usuario_atual:
                logger.warning(f"GestorRH não encontrado para email {request.user.email}")
                messages.error(request, "Erro: Usuário RH não registrado no sistema.")
                return redirect('rh:view_advertencia_rh', id=id)
            
            with transaction.atomic():
                # Registra a investigação no workflow
                WarningWorkflow.objects.create(
                    AdvertenciaID=advertencia,
                    GestorRH=usuario_atual,
                    Stage=WORKFLOW_STAGES['RH_AGENDA'],
                    Comments=f'Investigação iniciada: {descricao_investigacao}'
                )
                
                # Processa anexos da investigação
                arquivos = request.FILES.getlist('arquivos_investigacao')
                if arquivos:
                    for f in arquivos:
                        # Validar arquivo
                        is_valid, error_msg, file_type = validate_file_upload(f)
                        if not is_valid:
                            logger.warning(f"Arquivo inválido: {f.name} - {error_msg}")
                            continue
                        
                        if f.size <= 10 * 1024 * 1024:  # 10MB limit
                            WarningAttachments.objects.create(
                                AdvertenciaID=advertencia,
                                FileName=f"[INVESTIGAÇÃO] {f.name}",
                                FileType=file_type,
                                FilePath=f
                            )
                        else:
                            logger.warning(f"Arquivo {f.name} ultrapassa 10MB")
                            messages.warning(request, f" Arquivo {f.name} é muito grande (máximo 10MB)")
            
            logger.info(f"Investigação iniciada para advertência {id} por {request.user.email}")
            messages.success(request, "Investigação registrada com sucesso!")
            return redirect('rh:view_advertencia_rh', id=id)
        
        except Exception as e:
            logger.error(f"Erro ao registrar investigação de {id}: {str(e)}")
            messages.error(request, f"Erro ao registrar investigação: {str(e)}")
            return redirect('rh:view_advertencia_rh', id=id)
    
    return redirect('rh:view_advertencia_rh', id=id)


# --- VIEW DE AGENDAMENTO E CONCLUSÃO ---
@login_required
def schedule_and_conclude(request, id):
    """
    Agenda a data de aplicação da advertência e finaliza em concluida.
    Só funciona quando a advertência está no status aprovada.
    """
    advertencia = get_object_or_404(Warnings, pk=id, Active=True, CurrentStage=WARNING_STAGES['APROVADA'])
    
    if request.method == 'POST':
        data_aplicacao = request.POST.get('data_aplicacao', '').strip()
        
        if not data_aplicacao:
            messages.error(request, "Por favor, selecione uma data de aplicação.")
            return redirect('rh:view_advertencia_rh', id=id)
        
        try:
            # Validar email do usuário
            is_valid, error_msg = validate_user_email(request.user)
            if not is_valid:
                messages.error(request, error_msg)
                return redirect('rh:view_advertencia_rh', id=id)
            
            usuario_atual = GestorRH.objects.filter(Email=request.user.email).first()
            if not usuario_atual:
                logger.warning(f"GestorRH não encontrado para email {request.user.email}")
                messages.error(request, "Erro: Usuário RH não registrado no sistema.")
                return redirect('rh:view_advertencia_rh', id=id)
            
            # Validar data
            is_valid, error_msg, scheduled_date = validate_date_schedule(data_aplicacao, min_days=1, max_days=30)
            if not is_valid:
                messages.error(request, error_msg)
                return redirect('rh:view_advertencia_rh', id=id)
            
            with transaction.atomic():
                # Atualiza o status e a data agendada
                advertencia.CurrentStage = WARNING_STAGES['CONCLUIDA']
                advertencia.ScheduledDate = scheduled_date
                advertencia.UpdatedAt = timezone.now()
                advertencia.save()
                
                # Registra a ação no workflow
                WarningWorkflow.objects.create(
                    AdvertenciaID=advertencia,
                    GestorRH=usuario_atual,
                    Stage=WORKFLOW_STAGES['RH_AGENDA'],
                    Comments=f'Advertência agendada para {scheduled_date}. Status finalizado pelo RH.'
                )
            
            logger.info(f"Advertência {id} agendada para {scheduled_date} por {request.user.email}")
            messages.success(request, f"Advertência agendada para {scheduled_date} e marcada como concluída!")
            return redirect('rh:advertencia')
        
        except Exception as e:
            logger.error(f"Erro ao agendar advertência {id}: {str(e)}")
            messages.error(request, f"Erro ao agendar advertência: {str(e)}")
            return redirect('rh:view_advertencia_rh', id=id)
    
    return redirect('rh:view_advertencia_rh', id=id)


# --- VIEW DE SINDICÂNCIA (DOCUMENTATION AND RESUBMISSION) ---
@login_required
def handle_sindicancia(request, id):
    """
    Permite ao RH adicionar documentação de sindicância (novas evidências)
    e detalhar motivo da sindicância quando a advertência volta após rejeição pela Diretoria.
    Status aceito: sindicancia
    """
    advertencia = get_object_or_404(Warnings, pk=id, Active=True, CurrentStage=WARNING_STAGES['SINDICANCIA'])
    
    if request.method == 'POST':
        detalhamento_sindicancia = request.POST.get('detalhamento_sindicancia', '').strip()
        
        if not detalhamento_sindicancia:
            messages.error(request, "Por favor, detalhe o motivo em relação à sindicância.")
            return redirect('rh:view_advertencia_rh', id=id)
        
        try:
            # Validar email do usuário
            is_valid, error_msg = validate_user_email(request.user)
            if not is_valid:
                messages.error(request, error_msg)
                return redirect('rh:view_advertencia_rh', id=id)
            
            usuario_atual = GestorRH.objects.filter(Email=request.user.email).first()
            if not usuario_atual:
                logger.warning(f"GestorRH não encontrado para email {request.user.email}")
                messages.error(request, "Erro: Usuário RH não registrado no sistema.")
                return redirect('rh:view_advertencia_rh', id=id)
            
            with transaction.atomic():
                # Registra a resposta à sindicância no workflow
                WarningWorkflow.objects.create(
                    AdvertenciaID=advertencia,
                    GestorRH=usuario_atual,
                    Stage=WORKFLOW_STAGES['REVISA_RH'],
                    Comments=f'Sindicância respondida: {detalhamento_sindicancia}'
                )
                
                # Processa anexos de sindicância (documentos novos para reenvio)
                arquivos = request.FILES.getlist('documentos_sindicancia')
                if arquivos:
                    for f in arquivos:
                        # Validar arquivo
                        is_valid, error_msg, file_type = validate_file_upload(f)
                        if not is_valid:
                            logger.warning(f"Arquivo inválido: {f.name} - {error_msg}")
                            continue
                        
                        if f.size <= 10 * 1024 * 1024:  # 10MB limit
                            WarningAttachments.objects.create(
                                AdvertenciaID=advertencia,
                                FileName=f"[SINDICÂNCIA] {f.name}",
                                FileType=file_type,
                                FilePath=f
                            )
                        else:
                            logger.warning(f"Arquivo {f.name} ultrapassa 10MB")
                            messages.warning(request, f"Arquivo {f.name} é muito grande (máximo 10MB)")
                
                logger.info(f"Sindicância documentada para advertência {id} por {request.user.email}")
                messages.success(request, "Sindicância documentada com sucesso!")
                return redirect('rh:view_advertencia_rh', id=id)
        
        except Exception as e:
            logger.error(f"Erro ao processar sindicância de {id}: {str(e)}")
            messages.error(request, f"Erro ao processar sindicância: {str(e)}")
            return redirect('rh:view_advertencia_rh', id=id)
    
    return redirect('rh:view_advertencia_rh', id=id)


# --- VIEW PARA ENVIAR SINDICÂNCIA DE VOLTA À DIRETORIA ---
@login_required
def send_sindicancia_to_diretoria(request, id):
    """
    Envia a advertência com documentação de sindicância de volta à Diretoria para reavaliação.
    Muda o status de sindicancia para analise_diretoria.
    """
    advertencia = get_object_or_404(Warnings, pk=id, Active=True, CurrentStage=WARNING_STAGES['SINDICANCIA'])
    
    try:
        # Validar email do usuário
        is_valid, error_msg = validate_user_email(request.user)
        if not is_valid:
            messages.error(request, error_msg)
            return redirect('rh:view_advertencia_rh', id=id)
        
        usuario_atual = GestorRH.objects.filter(Email=request.user.email).first()
        if not usuario_atual:
            logger.warning(f"GestorRH não encontrado para email {request.user.email}")
            messages.error(request, "Erro: Usuário RH não registrado no sistema.")
            return redirect('rh:view_advertencia_rh', id=id)
        
        # Validar transição de estado
        is_valid, error_msg = validate_state_transition(
            advertencia.CurrentStage,
            WARNING_STAGES['ANALISE_DIRETORIA']
        )
        if not is_valid:
            messages.error(request, error_msg)
            return redirect('rh:view_advertencia_rh', id=id)
        
        with transaction.atomic():
            # Atualiza o status para análise diretoria novamente
            advertencia.CurrentStage = WARNING_STAGES['ANALISE_DIRETORIA']
            advertencia.UpdatedAt = timezone.now()
            advertencia.save()
            
            # Registra a ação no workflow
            WarningWorkflow.objects.create(
                AdvertenciaID=advertencia,
                GestorRH=usuario_atual,
                Stage=WORKFLOW_STAGES['ENVIA_DIRETORIA'],
                Comments='Advertência com sindicância documentada encaminhada novamente para Diretoria.'
            )
        
        logger.info(f"Sindicância encaminhada para Diretoria por {request.user.email}")
        messages.success(request, "Sindicância encaminhada com sucesso para a Diretoria!")
        return redirect('rh:advertencia')
    
    except Exception as e:
        logger.error(f"Erro ao enviar sindicância {id} para Diretoria: {str(e)}")
        messages.error(request, f"Erro ao encaminhar sindicância: {str(e)}")
        return redirect('rh:view_advertencia_rh', id=id)
        messages.error(request, f"Erro ao encaminhar sindicância: {str(e)}")
        return redirect('rh:view_advertencia_rh', id=id)
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
        return redirect('rh:view_advertencia_rh', id=id)