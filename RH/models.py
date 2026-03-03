from argparse import FileType
from django.db import models
from django.contrib.auth.models import User


class Users(models.Model):
    UserID = models.AutoField(primary_key=True) #ID único para cada usuário
    Name = models.CharField(max_length=100) #Nome completo do usuário
    Email = models.EmailField(unique=True) #Email do usuário, deve ser único
    Department = models.CharField(max_length=100) #Departamento ao qual o usuário pertence
    Office365ID = models.CharField(max_length=100) #ID do usuário no Azure AD (Office 365)
    PhoneNumber = models.CharField(max_length=20, blank=True, null=True) #Número de telefone do usuário, opcional
    Active = models.BooleanField(default=True) #Indica se o usuário está ativo ou inativo no sistema


class Employees(models.Model):
    EmployeeID = models.AutoField(primary_key=True) #ID único para cada colaborador
    Name = models.CharField(max_length=100) #Nome completo do colaborador
    Department = models.CharField(max_length=100) #Departamento ao qual o colaborador pertence
    Position = models.CharField(max_length=100) #Cargo ou função do colaborador
    Email = models.EmailField(unique=True) #Email do colaborador, deve ser único
    PhoneNumber = models.CharField(max_length=20, blank=True, null=True) #Número de telefone do colaborador, opcional
    Active = models.BooleanField(default=True) #Indica se o colaborador está ativo ou inativo na empresa


class Warnings(models.Model):
    AdvertenciaID = models.AutoField(primary_key=True) #ID único para cada advertência
    Employee = models.ForeignKey(Employees, on_delete=models.CASCADE) #Relacionamento com o colaborador que recebeu a advertência
    WarningUserID = models.ForeignKey('Users', on_delete=models.CASCADE) #Relacionamento com o usuário que criou a advertência (solicitante)
    IncidentDate = models.DateField() #Data do ocorrido que motivou a advertência
    Description = models.TextField() #Descrição detalhada do motivo da advertência
    OfficialText = models.TextField() #Texto oficial da advertência, que pode ser preenchido após análise do RH
    CurrentStage = models.CharField(max_length=50) #Etapa atual do processo de advertência (Ex: "Em Análise RH", "Em Análise Diretoria", "Aprovada", "Concluída")
    SchenduledDate = models.DateField() #Data agendada para a próxima etapa ou para conclusão do processo
    CreatedAt = models.DateTimeField(auto_now_add=True) #Data e hora de criação da advertência
    UpdatedAt = models.DateTimeField(auto_now=True) #Data e hora da última atualização da advertência

class WarningWorkflow(models.Model):
    WorkflowID = models.AutoField(primary_key=True) #ID único para cada etapa do workflow
    AdvertenciaID = models.ForeignKey(Warnings, on_delete=models.CASCADE) #Relacionamento com a advertência à qual essa etapa do workflow pertence
    WarningWorkflowUserID = models.ForeignKey('Users', on_delete=models.CASCADE) #Relacionamento com o usuário responsável por essa etapa do workflow
    Stage = models.CharField(max_length=50) #Etapa do processo (Ex: "Solicitação Criada", "Análise RH", "Análise Diretoria", "Aprovada", "Rejeitada", etc.)
    Comments = models.TextField(blank=True, null=True) #Comentários ou observações feitas pelo responsável nessa etapa do workflow
    CreatedAt = models.DateTimeField(auto_now_add=True) #Data e hora de criação dessa etapa do workflow

class WarningAttachments(models.Model):
    AttachmentID = models.AutoField(primary_key=True) #ID único para cada anexo relacionado a uma advertência
    AdvertenciaID = models.ForeignKey(Warnings, on_delete=models.CASCADE) #Relacionamento com a advertência à qual esse anexo pertence
    FileName = models.CharField(max_length=255) #Nome original do arquivo anexado
    FilePath = models.FileField(upload_to='advertencias/anexos/') #Caminho onde o arquivo está armazenado no servidor
    FileType = models.CharField(max_length=50) #Tipo do arquivo (Ex: "pdf", "jpg", "docx", etc.)
    CreatedAt = models.DateTimeField(auto_now_add=True) #Data e hora de criação do registro de anexo

class InvestigationProcess(models.Model):
    InvestigationID = models.AutoField(primary_key=True) #ID único para cada processo de investigação relacionado a uma advertência
    AdvertenciaID = models.ForeignKey(Warnings, on_delete=models.CASCADE) #Relacionamento com a advertência à qual esse processo de investigação pertence
    Description = models.TextField() #Descrição detalhada do processo de investigação.
    Conclusion = models.TextField(blank=True, null=True) #Conclusão do processo de investigação, preenchida após a análise final do caso
    Status = models.CharField(max_length=50) #Status atual do processo de investigação (Ex: "Em Andamento", "Concluído", "Rejeitado", etc.)
    UserID = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='investigation_user') #Relacionamento com o usuário responsável por conduzir o processo de investigação
    LastUpdatetByID = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='investigation_last_updated_by') #Relacionamento com o usuário que realizou a última atualização no processo de investigação

class InvestigationAttachments(models.Model):
    AttachmentID = models.AutoField(primary_key=True) #ID único para cada anexo relacionado a um processo de investigação
    InvestigationID = models.ForeignKey(InvestigationProcess, on_delete=models.CASCADE) #Relacionamento com o processo de investigação ao qual esse anexo pertence
    OriginalFileName = models.CharField(max_length=255) #Nome original do arquivo anexado
    StoredFileName = models.CharField(max_length=255) #Nome do arquivo armazenado no servidor (pode ser diferente do nome original para evitar conflitos)
    Token = models.CharField(max_length=255) #Token único para acesso seguro ao arquivo, caso seja necessário compartilhar ou acessar o arquivo de forma controlada
    UploadedByID = models.ForeignKey(Users, on_delete=models.CASCADE) #Relacionamento com o usuário que fez o upload do arquivo
    UploadedAt = models.DateTimeField(auto_now_add=True) #Data e hora de upload do arquivo
