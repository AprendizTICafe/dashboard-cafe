from django.shortcuts import render, redirect, get_object_or_404
from .models import Colaborador, Warnings, WarningWorkflow, Gestor, WarningAttachments
from TI.models import Warnings as AdvertenciaTI
from django.contrib import messages
from django.db import IntegrityError
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.utils import timezone


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

        if not email or not nome:
            messages.error(request, "Nome e E-mail são obrigatórios.")
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

    context = {
        # Conta advertências com base no status exato salvo na criação
        'advertencias_solicitadas': AdvertenciaTI.objects.filter(Active=True, CurrentStage='Solicitada').count(),
        'advertencias_em_analise_rh': Warnings.objects.filter(Active=True, CurrentStage='Em Análise RH').count(),
        'advertencias_em_analise_diretoria': Warnings.objects.filter(Active=True, CurrentStage='Em Análise Diretoria').count(),
        'advertencias_aprovadas': Warnings.objects.filter(Active=True, CurrentStage='Aprovada').count(),
        'advertencias_concluidas': Warnings.objects.filter(Active=True, CurrentStage='Concluída').count(),
        
        # Filtra as advertências ativas e solicitadas, pegando as 10 últimas.
        'ultimas_advertencias': AdvertenciaTI.objects.filter(Active=True, CurrentStage='Solicitada').order_by('-CreatedAt')[:10],
        
        # Necessário para popular o select do formulário dentro do portal
        'colaboradores': Colaborador.objects.filter(Active=True).order_by('Name'),
    }
    return render(request, 'RH/advertencia.html', context)

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
        colaborador = get_object_or_404(Colaborador, ColaboradorID=request.POST.get('colaborador'))

        try:
            # Iniciamos uma transação atômica: ou salva tudo (adv + anexos + workflow) ou nada
            with transaction.atomic():
                
                # 3. Criação do registro principal de Advertência
                nova_war = Warnings.objects.create(
                    ColaboradorID=colaborador,
                    WarningUserID=solicitante, # Chave estrangeira para o modelo Users
                    IncidentDate=request.POST.get('data_ocorrência'),
                    Description=request.POST.get('descricao'), 
                    CurrentStage="Solicitada", # Status que bate com o filtro do portal
                    SchenduledDate=request.POST.get('data_ocorrência') 
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
                    WarningWorkflowUserID=solicitante,
                    Stage="Solicitada",
                    Comments="Solicitação de advertência criada",
                    CreatedAt=timezone.now()
                )

            # Se chegou aqui, deu tudo certo
            messages.success(request, "Solicitação de advertência enviada com sucesso!")
            return redirect('rh:advertencia') # Redireciona para atualizar as estatísticas

        except Exception as e:
            # Em caso de erro, exibe a mensagem e volta ao portal
            messages.error(request, f"Erro ao processar solicitação: {e}")
            return redirect('rh:advertencia')

    # --- Lógica para GET (Exibir formulário) ---
    # O RH tem acesso a selecionar todos os colaboradores ativos
    colaboradores = Colaborador.objects.filter(Active=True)

    
    return render(request, 'RH/nova_advertencia.html', {'colaboradores': colaboradores.order_by('Name')})


def advertencia_list(request):
    # 1. Lista todos os colaboradores para o <select> do filtro e retorna base geral, pois é o portal do RH
    try:
        # Lista de colaboradores para o <select> do filtro
        colaboradores_dept = Colaborador.objects.filter(Active=True).order_by('Name')
        queryset = Warnings.objects.filter(Active=True)
    except AttributeError:
        colaboradores_dept = Colaborador.objects.none()
        queryset = Warnings.objects.none()

    # 2. Captura os filtros
    ColaboradorID = request.GET.get('colaborador') # Agora recebemos o ID (PK)
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
    return render(request, 'rh/advertencia.html', context)