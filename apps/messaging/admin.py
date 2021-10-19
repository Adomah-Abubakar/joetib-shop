from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Sms, Contact
# Register your models here.
@admin.register(Contact)
class ContactAdmin(ImportExportModelAdmin):
    pass
@admin.register(Sms)
class SmsAdmin(ImportExportModelAdmin):
    pass


class ContactResource(resources.ModelResource):
    class Meta:
        model = Contact


class SmsResource(resources.ModelResource):
    class Meta:
        model = Sms

