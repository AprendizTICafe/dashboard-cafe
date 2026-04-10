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

    context = {
        # Conta advertências com base no status exato salvo na criação
        'advertencias_solicitadas': Warnings.objects.filter(DepartmentOrigin="Logística", Active=True, CurrentStage='criada').count(),
        'advertencias_em_analise_rh': Warnings.objects.filter(DepartmentOrigin="Logística", Active=True, CurrentStage='analise_rh').count(),
        'advertencias_em_analise_diretoria': Warnings.objects.filter(DepartmentOrigin="Logística", Active=True, CurrentStage='analise_diretoria').count(),
        'advertencias_aprovadas': Warnings.objects.filter(DepartmentOrigin="Logística", Active=True, CurrentStage='aprovada').count(),
        'advertencias_concluidas': Warnings.objects.filter(DepartmentOrigin="Logística", Active=True, CurrentStage='concluida').count(),
        
        # Filta as advertências ativas e filtra as 10 últimas.
        'ultimas_advertencias': Warnings.objects.filter(DepartmentOrigin="Logística", Active=True).order_by('-CreatedAt')[:10],
        
        # Necessário para popular o select do formulário dentro do portal
        'colaboradores': Colaborador.objects.filter(Active=True).order_by('Name'),
    }
    return render(request, 'Logistica/advertencia.html', context)


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

        try:
            # Iniciamos uma transação atômica: ou salva tudo (adv + anexos + workflow) ou nada
            with transaction.atomic():
                
                # 3. Criação do registro principal de Advertência
                nova_war = Warnings.objects.create(
                    ColaboradorID=colaborador,
                    DepartmentOrigin="Logística",
                    Gestor=usuario,  
                    IncidentDate=request.POST.get('data_ocorrencia'),
                    Description=request.POST.get('Descricao'), 
                    CurrentStage="criada",
                    SchenduledDate=request.POST.get('data_ocorrencia')
                )

                # 4. Processamento de múltiplos arquivos anexos
                arquivos = request.FILES.getlist('arquivos')
                for f in arquivos:
                    # Filtro de tamanho (opcional, mas recomendado)
                    if f.size <= 10 * 1024 * 1024:
                        WarningAttachments.objects.create(
                            AdvertenciaID=nova_war,
                            FileName=f.name,
                            FileType=f.content_type.split('/')[-1], # Salva 'pdf', 'png', etc.
                            FilePath=f # O Django cuida do upload para a pasta MEDIA
                        )

                # 5. Registro do primeiro passo no histórico (Workflow)
                WarningWorkflow.objects.create(
                    AdvertenciaID=nova_war,
                    Stage="Solicitada",
                    Comments="Solicitação de advertência criada."
                )

            # Se chegou aqui, deu tudo certo
            messages.success(request, "Solicitação de advertência criada com sucesso!")
            return redirect('logistica:advertencia') # Redireciona para atualizar as estatísticas

        except Exception as e:
            # Em caso de erro, exibe a mensagem e volta ao portal
            messages.error(request, f"Erro ao processar solicitação: {e}")
            return redirect('logistica:advertencia')

    # --- Lógica para GET (Exibir formulário) ---
    # Filtramos diretamente pelo departamento de Logística e colaboradores ativos
    # Isso garante que a lista apareça mesmo se o Gestor não tiver cadastro na tabela Logistica.models.Gestor ainda
    colaboradores = Colaborador.objects.filter(Department="Logística", Active=True)

    return render(request, 'Logistica/nova_advertencia.html', {'colaboradores': colaboradores.order_by('Name')})

def advertencia_list(request):
    # 1. Filtra por departamento de Logística (para o app Logistica)
    # Lista de colaboradores para o <select> do filtro
    colaboradores_dept = Colaborador.objects.filter(Department="Logística", Active=True).order_by('Name')
    queryset = Warnings.objects.filter(DepartmentOrigin="Logística")

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
    return render(request, 'Logistica/advertencia.html', context)


# --- VIEW DE VISUALIZACIÓN DE DETALHES ---
@login_required
def view_advertencia(request, id):
    """
    Exibe os detalhes de uma advertência criada por Logística.
    Apenas o criador da advertência pode enviá-la para o RH.
    """
    advertencia = get_object_or_404(Warnings, pk=id, Active=True)
    anexos = WarningAttachments.objects.filter(AdvertenciaID=advertencia)
    workflow = WarningWorkflow.objects.filter(AdvertenciaID=advertencia).order_by('-CreatedAt')
    
    # Verifica se o usuário logado é o criador da advertência
    email_usuario = request.user.email
    pode_enviar = (advertencia.Gestor and advertencia.Gestor.email == email_usuario and 
                  advertencia.CurrentStage == 'criada')
    
    context = {
        'advertencia': advertencia,
        'anexos': anexos,
        'workflow': workflow,
        'pode_enviar': pode_enviar,
    }
    return render(request, 'Logistica/detalhes_advertencia.html', context)


# --- VIEW DE ENVIO PARA RH ---
@login_required
def send_to_rh(request, id):
    """
    Envia a advertência de Logística para análise do RH.
    Muda o status de "criada" para "analise_rh".
    """
    advertencia = get_object_or_404(Warnings, pk=id, Active=True)
    
    # Verifica se o usuário logado é o criador e se o status permite
    email_usuario = request.user.email
    if not email_usuario:
        messages.error(request, "Erro: Usuário sem email configurado.")
        return redirect('logistica:advertencia')

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
        return redirect('logistica:advertencia')
    
    except Exception as e:
        messages.error(request, f"Erro ao enviar advertência: {str(e)}")
        return redirect('logistica:view_advertencia', id=id)


def excluir_advertencia(request, id):
    if request.method == 'POST':
        advertencia = get_object_or_404(Warnings, pk=id)
        
        # Apenas muda o status para invisível
        advertencia.Active = False
        advertencia.save()
        
        messages.success(request, "Advertência removida da visualização.")
            
    return redirect('logistica:advertencia')
