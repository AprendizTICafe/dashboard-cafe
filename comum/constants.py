"""
Constantes centralizadas do sistema de advertências.
Evita hardcoding de strings e garante consistência entre apps.
"""

# Estágios das Advertências (CurrentStage)
WARNING_STAGES = {
    'SOLICITADA': 'solicitada',
    'ANALISE_RH': 'analise_rh',
    'ANALISE_DIRETORIA': 'analise_diretoria',
    'APROVADA': 'aprovada',
    'SINDICANCIA': 'sindicancia',
    'CANCELADA': 'cancelada',
    'CONCLUIDA': 'concluida',
}

WARNING_STAGES_CHOICES = [
    (WARNING_STAGES['SOLICITADA'], 'Solicitada'),
    (WARNING_STAGES['ANALISE_RH'], 'Análise RH'),
    (WARNING_STAGES['ANALISE_DIRETORIA'], 'Análise Diretoria'),
    (WARNING_STAGES['APROVADA'], 'Aprovada'),
    (WARNING_STAGES['SINDICANCIA'], 'Sindicância'),
    (WARNING_STAGES['CANCELADA'], 'Cancelada'),
    (WARNING_STAGES['CONCLUIDA'], 'Concluída'),
]

# Estágios do Workflow (histórico de ações)
WORKFLOW_STAGES = {
    'CRIADA': 'criada',
    'REVISA_RH': 'revisa_rh',
    'ENVIA_DIRETORIA': 'envia_diretoria',
    'DIRETORIA_APROVA': 'diretoria_aprova',
    'DIRETORIA_REPROVA': 'diretoria_reprova',
    'RH_AGENDA': 'rh_agenda',
    'RH_CANCELA': 'rh_cancela',
    'CONCLUIDA': 'concluida',
}

WORKFLOW_STAGES_CHOICES = [
    (WORKFLOW_STAGES['CRIADA'], 'Solicitação Criada'),
    (WORKFLOW_STAGES['REVISA_RH'], 'RH Revisou'),
    (WORKFLOW_STAGES['ENVIA_DIRETORIA'], 'RH Enviou para Diretoria'),
    (WORKFLOW_STAGES['DIRETORIA_APROVA'], 'Diretoria Aprovou'),
    (WORKFLOW_STAGES['DIRETORIA_REPROVA'], 'Diretoria Reprovou'),
    (WORKFLOW_STAGES['RH_AGENDA'], 'RH Agendou'),
    (WORKFLOW_STAGES['RH_CANCELA'], 'RH Cancelou'),
    (WORKFLOW_STAGES['CONCLUIDA'], 'Concluída'),
]

# Departamentos do Sistema
DEPARTMENTS = {
    'TI': 'Tecnologia da Informação',
    'FINANCEIRO': 'Financeiro',
    'CONTABILIDADE': 'Contabilidade',
    'DIRETORIA': 'Diretoria',
    'LOGISTICA': 'Logística',
    'MANUTENCAO': 'Manutenção',
    'MARKETING': 'Marketing',
    'SEGURANCA_TRABALHO': 'Segurança do Trabalho',
}

# Mapeamento de departamentos para seus modelos de Gestor
# Usado em RH/signals.py para roteamento dinâmico
DEPARTMENT_MODELS = {
    DEPARTMENTS['TI']: 'TI.GestorTI',
    DEPARTMENTS['FINANCEIRO']: 'Financeiro.GestorFinanceiro',
    DEPARTMENTS['CONTABILIDADE']: 'Contabilidade.GestorContabilidade',
    DEPARTMENTS['DIRETORIA']: 'Diretoria.GestorDiretoria',
    DEPARTMENTS['LOGISTICA']: 'Logistica.GestorLogistica',
    DEPARTMENTS['MANUTENCAO']: 'Manutencao.GestorManutencao',
    DEPARTMENTS['MARKETING']: 'Marketing.GestorMarketing',
    DEPARTMENTS['SEGURANCA_TRABALHO']: 'SegurancaTrabalho.GestorSegurancaTrabalho',
}

# Transições válidas entre estágios (máquina de estado)
VALID_TRANSITIONS = {
    WARNING_STAGES['SOLICITADA']: [
        WARNING_STAGES['ANALISE_RH'],
        WARNING_STAGES['CANCELADA'],
    ],
    WARNING_STAGES['ANALISE_RH']: [
        WARNING_STAGES['ANALISE_DIRETORIA'],
        WARNING_STAGES['CANCELADA'],
    ],
    WARNING_STAGES['ANALISE_DIRETORIA']: [
        WARNING_STAGES['APROVADA'],
        WARNING_STAGES['CANCELADA'],
    ],
    WARNING_STAGES['APROVADA']: [
        WARNING_STAGES['SINDICANCIA'],
        WARNING_STAGES['CONCLUIDA'],
    ],
    WARNING_STAGES['SINDICANCIA']: [
        WARNING_STAGES['CONCLUIDA'],
        WARNING_STAGES['CANCELADA'],
    ],
    WARNING_STAGES['CANCELADA']: [],  # Terminal
    WARNING_STAGES['CONCLUIDA']: [],  # Terminal
}

# Operações de Workflow mapeadas para estágios
WORKFLOW_MAPPING = {
    'criar': WORKFLOW_STAGES['CRIADA'],
    'revisar_rh': WORKFLOW_STAGES['REVISA_RH'],
    'enviar_diretoria': WORKFLOW_STAGES['ENVIA_DIRETORIA'],
    'aprovar_diretoria': WORKFLOW_STAGES['DIRETORIA_APROVA'],
    'rejeitar_diretoria': WORKFLOW_STAGES['DIRETORIA_REPROVA'],
    'agendar_rh': WORKFLOW_STAGES['RH_AGENDA'],
    'cancelar_rh': WORKFLOW_STAGES['RH_CANCELA'],
    'concluir': WORKFLOW_STAGES['CONCLUIDA'],
}
