from django.db import models
from django.contrib.auth.models import User
from comum.models import Colaborador
from comum.constants import WARNING_STAGES_CHOICES, WORKFLOW_STAGES_CHOICES


class GestorRH(models.Model):
    """Membro do departamento de RH responsável por analisar advertências"""
    GestorID = models.AutoField(primary_key=True)  # ID único para cada usuário de RH
    Name = models.CharField(max_length=100)  # Nome completo do usuário
    Email = models.EmailField(unique=True)  # Email do usuário, deve ser único
    Office365ID = models.CharField(max_length=100)  # ID do usuário no Azure AD (Office 365)
    PhoneNumber = models.CharField(max_length=20, blank=True, null=True)  # Número de telefone do usuário, opcional
    Active = models.BooleanField(default=True)  # Indica se o usuário está ativo ou inativo no sistema

    def __str__(self):
        return f"{self.GestorID} - {self.Name} ({self.Email})"

    class Meta:
        verbose_name = "Gestor RH"
        verbose_name_plural = "Gestores RH"
        db_table = "RH_gestor_rh"


class Warnings(models.Model):
    """Tabela central de advertências do sistema"""
    
    AdvertenciaID = models.AutoField(primary_key=True)  # ID único para cada advertência
    ColaboradorID = models.ForeignKey(Colaborador, on_delete=models.CASCADE, related_name='rh_warnings')  # Relacionamento com o colaborador
    Gestor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Gestor que criou a advertência (pode ser de qualquer departamento)
    DepartmentOrigin = models.CharField(max_length=100)  # Departamento que solicitou a advertência (TI, Logística, etc)
    IncidentDate = models.DateField()  # Data do ocorrido que motivou a advertência
    Description = models.TextField()  # Descrição detalhada do motivo da advertência
    OfficialText = models.TextField(blank=True, null=True)  # Texto oficial da advertência, preenchido após análise do RH
    CurrentStage = models.CharField(max_length=50, choices=WARNING_STAGES_CHOICES)  # Etapa atual do processo
    GestorRH = models.ForeignKey(GestorRH, on_delete=models.SET_NULL, null=True, blank=True)  # Gestor RH responsável
    ScheduledDate = models.DateField(blank=True, null=True)  # Data agendada para a próxima etapa
    CreatedAt = models.DateTimeField(auto_now_add=True)  # Data e hora de criação da advertência
    UpdatedAt = models.DateTimeField(auto_now=True)  # Data e hora da última atualização
    Active = models.BooleanField(default=True)  # Indica se a advertência está ativa

    def __str__(self):
        return f"{self.AdvertenciaID} - {self.ColaboradorID.Name} - {self.get_CurrentStage_display()}"

    class Meta:
        verbose_name = "Advertência"
        verbose_name_plural = "Advertências"
        db_table = "RH_warnings"


class WarningWorkflow(models.Model):
    """Histórico de todas as etapas da advertência"""
    
    WorkflowID = models.AutoField(primary_key=True)  # ID único para cada etapa do workflow
    AdvertenciaID = models.ForeignKey(Warnings, on_delete=models.CASCADE, related_name='workflow_history')  # FK com a advertência
    Stage = models.CharField(max_length=50, choices=WORKFLOW_STAGES_CHOICES)  # Etapa do workflow
    GestorRH = models.ForeignKey(GestorRH, on_delete=models.SET_NULL, null=True, blank=True)  # Gestor RH responsável
    Comments = models.TextField(blank=True, null=True)  # Comentários ou observações
    CreatedAt = models.DateTimeField(auto_now_add=True)  # Data e hora da ação

    def __str__(self):
        return f"Etapa {self.AdvertenciaID.AdvertenciaID} - {self.get_Stage_display()}"

    class Meta:
        verbose_name = "Histórico de Workflow"
        verbose_name_plural = "Históricos de Workflow"
        db_table = "RH_warning_workflow"


class WarningAttachments(models.Model):
    AttachmentID = models.AutoField(primary_key=True)  # ID único para cada anexo relacionado a uma advertência
    AdvertenciaID = models.ForeignKey(Warnings, on_delete=models.CASCADE)  # Relacionamento com a advertência
    FileName = models.CharField(max_length=255)  # Nome original do arquivo anexado
    FilePath = models.FileField(upload_to='advertencias/anexos/')  # Caminho onde o arquivo está armazenado
    FileType = models.CharField(max_length=50)  # Tipo do arquivo (Ex: "pdf", "jpg", "docx", etc.)
    CreatedAt = models.DateTimeField(auto_now_add=True)  # Data e hora de criação do registro de anexo

    def __str__(self):
        return f"Anexo {self.AttachmentID} - {self.FileName}"

    class Meta:
        verbose_name = "Anexo"
        verbose_name_plural = "Anexos"
        db_table = "RH_warning_attachments"


class InvestigationProcess(models.Model):
    InvestigationID = models.AutoField(primary_key=True)  # ID único para cada processo de investigação
    AdvertenciaID = models.ForeignKey(Warnings, on_delete=models.CASCADE)  # Relacionamento com a advertência
    Description = models.TextField()  # Descrição detalhada do processo de investigação
    Conclusion = models.TextField(blank=True, null=True)  # Conclusão do processo de investigação
    Status = models.CharField(max_length=50)  # Status atual do processo de investigação
    UserID = models.ForeignKey(GestorRH, on_delete=models.CASCADE, related_name='investigation_user')  # Gestor RH responsável
    LastUpdatedByID = models.ForeignKey(GestorRH, on_delete=models.CASCADE, related_name='investigation_last_updated_by')  # Gestor RH que atualizou
    CreatedAt = models.DateTimeField(auto_now_add=True)  # Data e hora de criação
    UpdatedAt = models.DateTimeField(auto_now=True)  # Data e hora de atualização

    def __str__(self):
        return f"Investigação {self.InvestigationID} - {self.Status}"

    class Meta:
        verbose_name = "Processo de Investigação"
        verbose_name_plural = "Processos de Investigação"
        db_table = "RH_investigation_process"


class InvestigationAttachments(models.Model):
    AttachmentID = models.AutoField(primary_key=True)  # ID único para cada anexo de investigação
    InvestigationID = models.ForeignKey(InvestigationProcess, on_delete=models.CASCADE)  # FK com o processo de investigação
    OriginalFileName = models.CharField(max_length=255)  # Nome original do arquivo anexado
    StoredFileName = models.CharField(max_length=255)  # Nome do arquivo armazenado no servidor
    Token = models.CharField(max_length=255)  # Token único para acesso seguro ao arquivo
    UploadedByID = models.ForeignKey(GestorRH, on_delete=models.CASCADE)  # Gestor RH que fez o upload
    UploadedAt = models.DateTimeField(auto_now_add=True)  # Data e hora de upload do arquivo

    def __str__(self):
        return f"Anexo Investigação {self.AttachmentID} - {self.OriginalFileName}"

    class Meta:
        verbose_name = "Anexo de Investigação"
        verbose_name_plural = "Anexos de Investigação"
        db_table = "RH_investigation_attachments"

