from django.contrib import admin
from .models import Employees, Warnings, WarningWorkflow, Users, WarningAttachments

admin.site.register(Employees)
admin.site.register(Warnings)
admin.site.register(WarningWorkflow)
admin.site.register(Users)
admin.site.register(WarningAttachments)
