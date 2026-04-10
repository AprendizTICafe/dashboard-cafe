from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    numero = models.CharField(max_length=20, blank=True, null=True)
    nome = models.CharField(max_length=255, blank=True, null=True)
    segundo_nome = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    office365_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    ativo = models.BooleanField(default=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    cargo = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.user.username}) - {self.department} - {self.cargo}"

    class Meta:
        verbose_name = "Perfil do Usuário"
        verbose_name_plural = "Perfis dos Usuários"