from django.contrib import admin
from .models import Colaborador


@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('ColaboradorID', 'Name', 'Department', 'Position', 'Email', 'Active')
    search_fields = ('Name', 'Email', 'Department')
    list_filter = ('Active', 'Department')
