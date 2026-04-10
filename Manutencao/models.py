from django.db import models
from comum.models import Colaborador


class GestorManutencao(models.Model):
    """Gestor do departamento de Manutenção"""
    GestorID = models.AutoField(primary_key=True)  # ID único para cada gestor de Manutenção
    Name = models.CharField(max_length=100)  # Nome completo do gestor
    Email = models.EmailField(unique=True)  # Email do gestor, deve ser único
    Office365ID = models.CharField(max_length=100)  # ID do gestor no Azure AD (Office 365)
    PhoneNumber = models.CharField(max_length=20, blank=True, null=True)  # Número de telefone, opcional
    Active = models.BooleanField(default=True)  # Indica se o gestor está ativo

    def __str__(self):
        return f"{self.GestorID} - {self.Name} ({self.Email}) - Manutenção"

    class Meta:
        verbose_name = "Gestor Manutenção"
        verbose_name_plural = "Gestores Manutenção"
        db_table = "manutencao_gestor_manutencao"


class WarningRequest(models.Model):
    """Solicitação de advertência criada pelo Gestor de Manutenção"""
    REQUEST_STATUS = [
        ('criada', 'Criada'),
        ('enviada_rh', 'Enviada para RH'),
        ('convertida', 'Convertida em Advertência'),
        ('processando', 'Processando'),
    ]
    
    RequestID = models.AutoField(primary_key=True)  # ID único da solicitação
    GestorManutencao = models.ForeignKey(GestorManutencao, on_delete=models.CASCADE)  # Gestor Manutenção responsável
    ColaboradorID = models.ForeignKey(Colaborador, on_delete=models.CASCADE, related_name='manutencao_warning_requests')  # Colaborador que será advertido
    IncidentDate = models.DateField()  # Data do incidente
    Description = models.TextField()  # Descrição do motivo da advertência
    Status = models.CharField(max_length=50, choices=REQUEST_STATUS, default='criada')  # Status da solicitação
    AdvertenciaID = models.ForeignKey('RH.Warnings', on_delete=models.SET_NULL, null=True, blank=True)  # ID da advertência criada no RH (quando convertida)
    CreatedAt = models.DateTimeField(auto_now_add=True)  # Data e hora de criação
    UpdatedAt = models.DateTimeField(auto_now=True)  # Data e hora de atualização

    def __str__(self):
        return f"Solicitação {self.RequestID} - {self.ColaboradorID.Name} - {self.get_status_display()}"

    class Meta:
        verbose_name = "Solicitação de Advertência"
        verbose_name_plural = "Solicitações de Advertência"
        db_table = "manutencao_warning_request"
