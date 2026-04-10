from django.contrib import admin
from .models import (
    GestorRH, Warnings, WarningWorkflow, 
    WarningAttachments, InvestigationProcess, InvestigationAttachments
)


@admin.register(GestorRH)
class GestorRHAdmin(admin.ModelAdmin):
    list_display = ('GestorID', 'Name', 'Email', 'Active')
    search_fields = ('Name', 'Email')
    list_filter = ('Active',)


@admin.register(Warnings)
class WarningsAdmin(admin.ModelAdmin):
    list_display = ('AdvertenciaID', 'ColaboradorID', 'DepartmentOrigin', 'CurrentStage', 'CreatedAt')
    search_fields = ('ColaboradorID__Name', 'DepartmentOrigin', 'AdvertenciaID')
    list_filter = ('CurrentStage', 'DepartmentOrigin', 'CreatedAt')
    readonly_fields = ('CreatedAt', 'UpdatedAt')


@admin.register(WarningWorkflow)
class WarningWorkflowAdmin(admin.ModelAdmin):
    list_display = ('WorkflowID', 'AdvertenciaID', 'Stage', 'CreatedAt')
    search_fields = ('AdvertenciaID__AdvertenciaID', 'Stage')
    list_filter = ('Stage', 'CreatedAt')
    readonly_fields = ('CreatedAt',)


@admin.register(WarningAttachments)
class WarningAttachmentsAdmin(admin.ModelAdmin):
    list_display = ('AttachmentID', 'AdvertenciaID', 'FileName', 'FileType', 'CreatedAt')
    search_fields = ('FileName', 'AdvertenciaID__AdvertenciaID')
    list_filter = ('FileType', 'CreatedAt')
    readonly_fields = ('CreatedAt',)


@admin.register(InvestigationProcess)
class InvestigationProcessAdmin(admin.ModelAdmin):
    list_display = ('InvestigationID', 'AdvertenciaID', 'Status', 'UserID', 'CreatedAt')
    search_fields = ('AdvertenciaID__AdvertenciaID', 'Status')
    list_filter = ('Status', 'CreatedAt')
    readonly_fields = ('CreatedAt', 'UpdatedAt')


@admin.register(InvestigationAttachments)
class InvestigationAttachmentsAdmin(admin.ModelAdmin):
    list_display = ('AttachmentID', 'InvestigationID', 'OriginalFileName', 'UploadedAt')
    search_fields = ('OriginalFileName', 'InvestigationID__InvestigationID')
    list_filter = ('UploadedAt',)
    readonly_fields = ('UploadedAt',)


