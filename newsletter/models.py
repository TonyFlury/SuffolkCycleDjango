from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
from django.conf import settings
from django.core.urlresolvers import reverse

# Create your models here.


class NewsletterRecipient(models.Model):
    """ Record the email addresses of everyone to send the NewsletterRecipient too """
    email = models.EmailField(unique=True)


class Newsletter(models.Model):
    pub_date = models.DateField( default=now, db_index=True )
    content = models.FileField( upload_to="newsletters/%Y/%m/%d/")
    title = models.CharField( max_length=80, default="" )

    def __str__(self):
        return "{}, {} ({}}".format(self.title, self.pub_date, self.content)