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
    user = models.ForeignKey(to=User, null=True)
    user_agent = models.CharField(max_length=80)
    arguments = DictField()

    @staticmethod
    def record(request, document_name=None, sub_document=None, private=False):

        namespace, url_name = request.resolver_match.namespace, request.resolver_match.url_name

        document_name = document_name if document_name else ("{}:{}".format(namespace,url_name) if namespace else url_name)
        visit = PageVisit.objects.create(
                document=document_name,
                sub_document=sub_document,
                source_ip=get_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', 'unknown'),
                user=request.user if request.user.is_authenticated() else None,
                arguments=dict() if private else (request.GET if request.GET else request.POST))
        visit.save()

    def __str__(self):
        return '{} visited {} (User: {})'.format(self.document, self.timestamp, self.user)

    @staticmethod
    def most_recent(document=None,**kwargs):
        """Find the most recent Page Visit - optionally matching document and sub_document
        :param document : Optional - The document to match on
        :param kwargs : Options further filters for this search
        :return : A PageVisit Instance or None
        """
        try:
            if document and not kwargs:
                return PageVisit.objects.filter(document=document).order_by('-timestamp')[0]
            elif document and kwargs:
                return PageVisit.objects.filter(document=document, **kwargs).order_by('-timestamp')[0]
            else:
                return PageVisit.objects.all().order_by('-timestamp')[0]
        except IndexError:
            return None
