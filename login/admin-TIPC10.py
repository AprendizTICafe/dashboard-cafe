from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['nome', 'segundo_nome', 'email', 'office365_id', 'ativo', 'department', 'cargo']
    list_filter = ['ativo', 'department', 'cargo']
    search_fields = ['nome', 'segundo_nome', 'email', 'user__username', 'office365_id']
    readonly_fields = ['office365_id', 'user']
    
    fieldsets = (
        ('Usuário', {
            'fields': ('user', 'numero')
        }),
        ('Dados Pessoais', {
            'fields': ('nome', 'segundo_nome', 'email', 'office365_id')
        }),
        ('Corporativo', {
            'fields': ('department', 'cargo', 'ativo')
        }),
    )
