from django.contrib import admin

import models
from markitup.widgets import AdminMarkItUpWidget


class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'max_value')
    prepopulated_fields = {"slug": ("name",)}

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'description':
            kwargs['widget'] = AdminMarkItUpWidget()
        return super(OpportunityAdmin, self).formfield_for_dbfield(db_field, **kwargs)


class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name', 'potential', )
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(models.Opportunity, OpportunityAdmin)
admin.site.register(models.Sponsor, SponsorAdmin)
