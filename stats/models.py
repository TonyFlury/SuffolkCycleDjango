from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from ipware.ip import get_ip

from fields import DictField

class PageVisit(models.Model):
    document = models.CharField(max_length=80, default='home')
    sub_document = models.CharField(max_length=80, null=True)
    timestamp = models.DateTimeField(default=now)
    source_ip = models.GenericIPAddressField()
    user = models.ForeignKey(to=User,null=True)
    user_agent = models.CharField(max_length=80)
    arguments = DictField()

    @staticmethod
    def record(request, document_name = None, sub_document = None):
        visit = PageVisit.objects.create(
                                document = document_name if document_name else request.resolver_match.url_name,
                                sub_document = sub_document,
                                source_ip = get_ip(request),
                                user_agent = request.META['HTTP_USER_AGENT'],
                                user = request.user if request.user.is_authenticated() else None,
                                arguments = request.GET if request.GET else request.POST )
        visit.save()

    def __str__(self):
        return '{} visited {} (User: {})'.format(self.document, self.timestamp, self.user)