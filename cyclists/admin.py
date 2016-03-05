from django.contrib import admin

from models import Cyclist, Leg

class LegAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    fields = (('name'), ('date','morning', 'duration'), ('start','end','distanceKM'), 'description')
    ordering = ('date', '-morning')
    list_display = ('date','morning', 'name','start','end', 'distanceKM')

class CyclistAdmin(admin.ModelAdmin):
    list_display = ('user',)

admin.site.register(Cyclist, CyclistAdmin)
admin.site.register(Leg, LegAdmin)

