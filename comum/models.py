from django.db import models


class Colaborador(models.Model):
    ColaboradorID = models.AutoField(primary_key=True)  # ID único para cada colaborador
    Name = models.CharField(max_length=100)  # Nome completo do colaborador
    Department = models.CharField(max_length=100)  # Departamento ao qual o colaborador pertence
    Position = models.CharField(max_length=100)  # Cargo ou função do colaborador
    Email = models.EmailField(unique=True)  # Email do colaborador, deve ser único
    PhoneNumber = models.CharField(max_length=20, blank=True, null=True)  # Número de telefone do colaborador, opcional
    Active = models.BooleanField(default=True)  # Indica se o colaborador está ativo ou inativo na empresa

    def __str__(self):
        return f"{self.ColaboradorID} - {self.Name} - ({self.Email}) - {self.Department}"

    class Meta:
        verbose_name = "Colaborador"
        verbose_name_plural = "Colaboradores"
        db_table = "comum_colaborador"
