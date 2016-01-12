from django.contrib import admin

from models import EmailQueue, EmailQueueAdmin

# Register your models here.

admin.site.register(EmailQueue, EmailQueueAdmin)