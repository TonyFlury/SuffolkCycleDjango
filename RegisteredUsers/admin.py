from django.contrib import admin

from models import PasswordResetRequest

class ResetRequestAdmin(admin.ModelAdmin):
    list_display=('user', 'uuid', 'expiry')


admin.site.register(PasswordResetRequest, ResetRequestAdmin)
