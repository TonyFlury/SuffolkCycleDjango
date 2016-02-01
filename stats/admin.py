from django.contrib import admin
from models import PageVisit


class PageVisitAdmin(admin.ModelAdmin):
    list_display=('document', 'sub_document', 'timestamp', 'user')


# Register your models here.
admin.site.register(PageVisit, PageVisitAdmin)
