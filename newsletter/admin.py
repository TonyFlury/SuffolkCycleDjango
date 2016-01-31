from django.contrib import admin

from models import NewsletterRecipient, Newsletter


class NewsletterAdmin(admin.ModelAdmin):
    list_display=('title', 'pub_date', 'content')


class NewsletterRecipientAdmin(admin.ModelAdmin):
    list_display=('email',)


# Register your models here.
admin.site.register(NewsletterRecipient, NewsletterRecipientAdmin)
admin.site.register(Newsletter, NewsletterAdmin)


