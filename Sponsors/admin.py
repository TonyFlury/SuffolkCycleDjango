from django.contrib import admin

from markitup.widgets import AdminMarkItUpWidget

import forms, models

class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'max_value')
    prepopulated_fields = {"slug": ("name",)}

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'description':
            kwargs['widget'] = AdminMarkItUpWidget()
        return super(OpportunityAdmin, self).formfield_for_dbfield(db_field, **kwargs)


class SponsorAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'contact_name', 'potential', )
    readonly_fields = ('slug',)
    fieldsets = (
          ('Name', {'fields': ('company_name', 'contact_name')}),
          ('Contact Details', {'fields':('email','telephone','mobile','communication_preference')}),
          ('Other Info', {'fields': ('website',)}),
          ('Logo', {'fields': ('logo_url','upload_logo')}),
          ('Sponsorship Status', {'fields':('potential',)}),
          ('Potentially Supports', {'fields': ('potentials',),
                                    'classes': ('collapse',)}),
          ('Actual Support', {'fields' : ('supports','accolade'),
                              'classes' : ('collapse',)})
                )
    form = forms.SponsorValidation


admin.site.register(models.Opportunity, OpportunityAdmin)
admin.site.register(models.Sponsor, SponsorAdmin)
