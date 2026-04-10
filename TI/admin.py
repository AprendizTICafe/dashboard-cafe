from django.contrib import admin
from .models import Colaborador, Warnings, WarningWorkflow, Gestor, WarningAttachments

admin.site.register(Colaborador)
admin.site.register(Warnings)
admin.site.register(WarningWorkflow)
admin.site.register(Gestor)
admin.site.register(WarningAttachments)
