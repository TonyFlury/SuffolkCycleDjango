from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from django.core.urlresolvers import reverse
import uuid

# No models - a view only implementation - use the default user model


class PasswordResetRequest(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    user = models.ForeignKey(to=User)
    expiry = models.DateField(default=now)

    def get_url(self):
        return reverse('User:Reset', args=[str(self.uuid)])
