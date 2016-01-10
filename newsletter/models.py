from __future__ import unicode_literals

from django.db import models

# Create your models here.

class NewsletterSignUp(models.Model):
    """ Record the email addresses of everyone to send the NewsletterSignUp too """
    email = models.EmailField()