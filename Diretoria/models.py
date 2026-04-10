from django.db import models


class GestorDiretoria(models.Model):
    """Membro da Diretoria responsável por aprovar ou reprovar advertências"""
    GestorID = models.AutoField(primary_key=True)  # ID único para cada membro da diretoria
    Name = models.CharField(max_length=100)  # Nome completo do membro
    Email = models.EmailField(unique=True)  # Email do membro, deve ser único
    Office365ID = models.CharField(max_length=100)  # ID do membro no Azure AD (Office 365)
    PhoneNumber = models.CharField(max_length=20, blank=True, null=True)  # Número de telefone, opcional
    Active = models.BooleanField(default=True)  # Indica se o membro está ativo

    def __str__(self):
        return f"{self.GestorID} - {self.Name} ({self.Email}) - Diretoria"

    class Meta:
        verbose_name = "Gestor Diretoria"
        verbose_name_plural = "Gestores Diretoria"
        db_table = "Diretoria_gestor_diretoria"

