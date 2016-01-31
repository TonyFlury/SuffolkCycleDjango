from django.contrib import admin

import models
from markitup.widgets import AdminMarkItUpWidget


class EntryAdmin(admin.ModelAdmin):
    list_display = ('title','pub_date','is_published', 'author')

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'content':
            kwargs['widget'] = AdminMarkItUpWidget()
        return super(EntryAdmin, self).formfield_for_dbfield(db_field, **kwargs)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(models.Entry, EntryAdmin)
admin.site.register(models.Tag, TagAdmin)
