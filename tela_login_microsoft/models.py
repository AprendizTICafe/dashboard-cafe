from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    department = models.CharField(max_length=255, blank=True, null=True)
    cargo = models.CharField(max_length=255, blank=True, null=True)

def __str__(self):
    return f"{self.user.username} - {self.department} - {self.cargo}"

class Departamento(models.Model):
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome

class Advertencia(models.Model):
    STATUS_CHOICES = [
        ('Solicitada', 'Solicitada'),
        ('Em Análise RH', 'Em Análise RH'),
        ('Em Análise Diretoria', 'Em Análise Diretoria'),
        ('Aprovada', 'Aprovada'),
        ('Concluída', 'Concluída'),
    ]

    GRAVIDADE_CHOICES = [
        ('Leve', 'Leve'),
        ('Média', 'Média'),
        ('Grave', 'Grave'),
    ]

    # Relacionamentos
    solicitante = models.ForeignKey(User, on_delete=models.PROTECT, related_name='advertencias_criadas')
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    
    # Dados do Colaborador que receberá a advertência
    colaborador_nome = models.CharField(max_length=255)
    colaborador_id_folha = models.CharField(max_length=50, verbose_name="ID ou Matrícula")
    
    # Detalhes da Ocorrência
    motivo = models.TextField()
    data_ocorrencia = models.DateField()
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    gravidade = models.CharField(max_length=10, choices=GRAVIDADE_CHOICES, default='Leve')
    
    # Fluxo de Aprovação
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Solicitada')
    observacao_rh = models.TextField(blank=True, null=True, verbose_name="Observações do RH")
    anexo = models.FileField(upload_to='advertencias/provas/', blank=True, null=True)

    class Meta:
        verbose_name = "Advertência"
        verbose_name_plural = "Advertências"
        ordering = ['-data_solicitacao']

    def __str__(self):
        return f"ADV#{self.id} - {self.colaborador_nome} ({self.status})"