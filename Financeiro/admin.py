from django.contrib import admin
from .models import GestorFinanceiro, WarningRequest


@admin.register(GestorFinanceiro)
class GestorFinanceiroAdmin(admin.ModelAdmin):
    list_display = ('GestorID', 'Name', 'Email', 'Active')
    search_fields = ('Name', 'Email')
    list_filter = ('Active',)


@admin.register(WarningRequest)
class WarningRequestAdmin(admin.ModelAdmin):
    list_display = ('RequestID', 'GestorFinanceiro', 'ColaboradorID', 'Status', 'CreatedAt')
    search_fields = ('ColaboradorID__Name', 'GestorFinanceiro__Name', 'RequestID')
    list_filter = ('Status', 'CreatedAt')
    readonly_fields = ('CreatedAt', 'UpdatedAt', 'AdvertenciaID')
