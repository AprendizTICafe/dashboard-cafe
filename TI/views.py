from django.shortcuts import render, redirect, get_object_or_404
from .models import Colaborador, Warnings, WarningWorkflow, Gestor, WarningAttachments
from django.contrib import messages
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from RH.models import Colaborador as ColaboradorRH
from django.utils import timezone

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
        'advertencias_em_analise_rh': Warnings.objects.filter(ColaboradorID__Department="Tecnologia da Informação", Active=True, CurrentStage='Em Análise RH').count(),
        'advertencias_em_analise_diretoria': Warnings.objects.filter(ColaboradorID__Department="Tecnologia da Informação", Active=True, CurrentStage='Em Análise Diretoria').count(),
        'advertencias_aprovadas': Warnings.objects.filter(ColaboradorID__Department="Tecnologia da Informação", Active=True, CurrentStage='Aprovada').count(),
        'advertencias_concluidas': Warnings.objects.filter(ColaboradorID__Department="Tecnologia da Informação", Active=True, CurrentStage='Concluída').count(),
        
        # Filta as advertências ativas e filtra as 10 últimas.
        'ultimas_advertencias': Warnings.objects.filter(ColaboradorID__Department="Tecnologia da Informação", Active=True).order_by('-CreatedAt')[:10],
        
        # Necessário para popular o select do formulário dentro do portal
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
        # 1. Identificação do Solicitante
        # Buscamos na nossa tabela de RH pelo e-mail do usuário logado no Django
        solicitante = Gestor.objects.filter(Email=request.user.email).first()

        # 2. Captura do Colaborador que receberá a advertência
        colaborador = get_object_or_404(ColaboradorRH, ColaboradorID=request.POST.get('colaborador'))

        try:
            # Iniciamos uma transação atômica: ou salva tudo (adv + anexos + workflow) ou nada
            with transaction.atomic():
                
                # 3. Criação do registro principal de Advertência
                nova_war = Warnings.objects.create(
                    ColaboradorID=colaborador, # Chave estrangeira para o modelo Colaborador
                    WarningUserID=solicitante, # Chave estrangeira para o modelo Users
                    IncidentDate=request.POST.get('data_ocorrencia'),
                    Description=request.POST.get('Descricao'), 
                    CurrentStage="Solicitada",
                    SchenduledDate=request.POST.get('data_ocorrencia')
                )

                # 4. Processamento de múltiplos arquivos anexos
                arquivos = request.FILES.getlist('arquivos')
                for f in arquivos:
                    # Filtro de tamanho (opcional, mas recomendado)
                    if f.size <= 10 * 1024 * 1024:
                        WarningAttachments.objects.create(
                            WarningID=nova_war,
                            FileName=f.name,
                            FileType=f.content_type.split('/')[-1], # Salva 'pdf', 'png', etc.
                            FilePath=f # O Django cuida do upload para a pasta MEDIA
                        )

                # 5. Registro do primeiro passo no histórico (Workflow)
                WarningWorkflow.objects.create(
                    WarningID=nova_war,
                    WarningWorkflowUserID=solicitante,
                    Stage="Solicitada",
                    Comments="Solicitação de advertência criada.",
                    CreatedAt=timezone.now()
                )

            # Se chegou aqui, deu tudo certo
            messages.success(request, "Solicitação de advertência enviada com sucesso!")
            return redirect('ti:advertencia') # Redireciona para atualizar as estatísticas

        except Exception as e:
            # Em caso de erro, exibe a mensagem e volta ao portal
            messages.error(request, f"Erro ao processar solicitação: {e}")
            return redirect('ti:advertencia')

    # --- Lógica para GET (Exibir formulário) ---
    # Filtramos diretamente pelo departamento de TI e colaboradores ativos
    # Isso garante que a lista apareça mesmo se o Gestor não tiver cadastro na tabela TI.models.Gestor ainda
    colaboradores = ColaboradorRH.objects.filter(Department="Tecnologia da Informação", Active=True)

    return render(request, 'TI/nova_advertencia.html', {'colaboradores': colaboradores.order_by('Name')})

def advertencia_list(request):
    # 1. Identifica o departamento do usuário logado
    try:
        user_dept = Gestor.objects.get(Email=request.user.email).Department
        # Lista de colaboradores para o <select> do filtro
        colaboradores_dept = Colaborador.objects.filter(Department=user_dept).order_by('Name')
        queryset = Warnings.objects.filter(ColaboradorID__Department=user_dept)
    except AttributeError:
        colaboradores_dept = Colaborador.objects.none()
        queryset = Warnings.objects.none()

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
    return render(request, 'ti/advertencia.html', context)


def excluir_advertencia(request, id):
    if request.method == 'POST':
        advertencia = get_object_or_404(Warnings, WarningID=id)
        
        # Apenas muda o status para invisível
        advertencia.Active = False
        advertencia.save()
        
        messages.success(request, "Advertência removida da visualização.")
            
    return redirect('ti:advertencia')
