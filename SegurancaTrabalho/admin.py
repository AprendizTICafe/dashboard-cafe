from django.contrib import admin
from .models import GestorSegurancaTrabalho, WarningRequest


@admin.register(GestorSegurancaTrabalho)
class GestorSegurancaTrabalhoAdmin(admin.ModelAdmin):
    list_display = ('GestorID', 'Name', 'Email', 'Active')
    search_fields = ('Name', 'Email')
    list_filter = ('Active',)


@admin.register(WarningRequest)
class WarningRequestAdmin(admin.ModelAdmin):
    list_display = ('RequestID', 'GestorSegurancaTrabalho', 'ColaboradorID', 'Status', 'CreatedAt')
    search_fields = ('ColaboradorID__Name', 'GestorSegurancaTrabalho__Name', 'RequestID')
    list_filter = ('Status', 'CreatedAt')
    readonly_fields = ('CreatedAt', 'UpdatedAt', 'AdvertenciaID')
