from django.contrib import admin

from models import Cyclist, Leg

class LegAdmin(admin.ModelAdmin):
    list_display = ('date','name','start','end', 'distanceKM')

class CyclistAdmin(admin.ModelAdmin):
    list_display = ('user',)

admin.site.register(Cyclist, CyclistAdmin)
admin.site.register(Leg, LegAdmin)

