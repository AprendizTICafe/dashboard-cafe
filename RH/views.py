from django.shortcuts import render, redirect, get_object_or_404
from .models import Employees, Warnings, WarningWorkflow, Users, WarningAttachments
from django.contrib import messages
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

# --- VIEW DO PORTAL (EXIBE AS ESTATÍSTICAS) ---
def portal(request):
    """
    Esta view calcula as contagens para os cards.
    Toda vez que o usuário é redirecionado para cá após um POST,
    os counts são refeitos, atualizando o número na tela.
    """
    context = {
        # Conta advertências com base no status exato salvo na criação
        'advertencias_solicitadas' : Warnings.objects.filter(CurrentStage='Solicitada').count(),
        'advertencias_em_analise_rh': Warnings.objects.filter(CurrentStage='Em Análise RH').count(),
        'advertencias_em_analise_diretoria': Warnings.objects.filter(CurrentStage='Em Análise Diretoria').count(),
        'advertencias_aprovadas': Warnings.objects.filter(CurrentStage='Aprovada').count(),
        'advertencias_concluidas': Warnings.objects.filter(CurrentStage='Concluída').count(),
        
        # Pega as 10 mais recentes para a lista de atividades
        'ultimas_advertencias': Warnings.objects.all().order_by('-CreatedAt')[:10],
        
        # Necessário para popular o select do formulário dentro do portal
        'colaboradores': Employees.objects.filter(Active=True).order_by('Name'),
    }
    return render(request, 'portal.html', context)


# --- VIEW DE CRIAÇÃO DA ADVERTÊNCIA ---
def nova_advertencia(request):
    """
    Processa o formulário de envio. Garante que o solicitante (Users)
    exista e esteja vinculado ao usuário logado (auth.User).
    """
    if request.method == "POST":
        # 1. Identificação do Solicitante
        # Buscamos na nossa tabela de RH pelo e-mail do usuário logado no Django
        solicitante = Users.objects.filter(Email=request.user.email).first()

        # Fallback de segurança: Se por algum motivo o Signal falhou, criamos o perfil agora
        if not solicitante:
            solicitante = Users.objects.create(
                Name=request.user.get_full_name() or request.user.username,
                Email=request.user.email,
                Office365ID=request.user.username,
                Active=True,
                Department="Geral" # Valor padrão inicial
            )

        # 2. Captura do Colaborador que receberá a advertência
        colaborador = get_object_or_404(Employees, EmployeeID=request.POST.get('colaborador'))

        try:
            # Iniciamos uma transação atômica: ou salva tudo (adv + anexos + workflow) ou nada
            with transaction.atomic():
                
                # 3. Criação do registro principal de Advertência
                nova_war = Warnings.objects.create(
                    Employee=colaborador,
                    WarningUserID=solicitante, # Chave estrangeira para o modelo Users
                    IncidentDate=request.POST.get('data_ocorrência'),
                    Description=request.POST.get('descricao'),
                    OfficialText="", 
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
                    Stage="Solicitação Criada",
                    Comments="Solicitação enviada via Portal."
                )

            # Se chegou aqui, deu tudo certo
            messages.success(request, "Solicitação de advertência enviada com sucesso!")
            return redirect('portal') # Redireciona para atualizar as estatísticas

        except Exception as e:
            # Em caso de erro, exibe a mensagem e volta ao portal
            messages.error(request, f"Erro ao processar solicitação: {e}")
            return redirect('portal')

    return render(request, 'nova_advertencia.html', {'colaboradores': Employees.objects.filter(Active=True).order_by('Name')})


# --- GATILHO (SIGNAL) DE SINCRONIZAÇÃO ---
@receiver(post_save, sender=User)
def criar_perfil_rh(sender, instance, created, **kwargs):
    """
    Sempre que um novo User for criado no Django (ex: via Admin ou Login Social),
    este gatilho cria automaticamente o perfil correspondente na tabela Users do RH.
    """
    if created:
        # Usamos getattr para tentar pegar o departamento, caso venha de um login externo,
        # se não existir, define como 'Geral'.
        departamento_extraido = getattr(instance, 'department')

        # get_or_create evita duplicidade caso o e-mail já exista
        Users.objects.get_or_create(
            Email=instance.email,
            defaults={
                'Name': instance.get_full_name() or instance.username,
                'Department': departamento_extraido,
                'Office365ID': instance.username,
                'Active': True
            }
        )

# --- VIEW DE CADASTRO DE NOVOS COLABORADORES (FUNCIONÁRIOS) ---
def cadastro_colaborador(request):
    """
    Recebe os dados do formulário de novos funcionários.
    Após o cadastro, redireciona para o portal para que o novo 
    colaborador já apareça na lista de seleção de advertências.
    """
    if request.method == "POST":
        # Coletando e limpando os dados (removendo espaços extras com strip)
        nome = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        telefone = request.POST.get('phone', '').strip()
        departamento = request.POST.get('department', '').strip()
        cargo = request.POST.get('position', '').strip()

        # Validação básica: impede e-mail vazio
        if not email:
            messages.error(request, "O campo de e-mail é obrigatório.")
            return redirect('cadastrar_colaborador')

        try:
            # get_or_create: tenta buscar pelo e-mail, se não existir, cria um novo.
            # 'colaborador' recebe o objeto, 'criado' recebe um booleano (True/False).
            colaborador, criado = Employees.objects.get_or_create(
                Email=email,
                defaults={
                    'Name': nome,
                    'PhoneNumber': telefone,
                    'Department': departamento,
                    'Position': cargo,
                    'Active': True
                }
            )

            if criado:
                messages.success(request, f"Colaborador {nome} cadastrado com sucesso!")
            else:
                messages.warning(request, f"O e-mail {email} já está vinculado ao colaborador {colaborador.Name}.")
            
            # Redirecionamos para o portal para atualizar a lista do formulário de advertência
            return redirect('portal') 

        except Exception as e:
            messages.error(request, f"Erro técnico ao cadastrar colaborador: {e}")
            return redirect('cadastro_colaborador')

    # Se o método for GET, apenas renderiza a página do formulário
    return render(request, 'cadastro_colaborador.html')