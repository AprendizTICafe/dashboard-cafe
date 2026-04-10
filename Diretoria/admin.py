from django.contrib import admin
from .models import GestorDiretoria


@admin.register(GestorDiretoria)
class GestorDiretoriaAdmin(admin.ModelAdmin):
    list_display = ('GestorID', 'Name', 'Email', 'Active')
    search_fields = ('Name', 'Email')
    list_filter = ('Active',)

