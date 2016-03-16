# coding=utf-8
from __future__ import unicode_literals
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models import fields
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.utils.text import slugify

from django.db.models.aggregates import Sum, Count

from urlparse import urlparse

import os.path

import hashlib
from decimal import Decimal

class HashedURLStorage(FileSystemStorage):
    """Simple extended FileSystemStorage class used for portrait pictures
        Ensures only one file of the appropriate name is stored.
        Also ensures that each file has either ?<hash> or &<hash> appended to ensure browser get
                a new file name when the file changes
    """
    def get_available_name(self, name, max_length):
        self.delete(name)
        return name

    def get_hash(self, name):
        m = hashlib.sha224()
        fp = self.open(name, 'rb')
        m.update(fp.read())
        fp.close()
        return m.hexdigest()[:8]

    def url(self, name):
        base_url = super(HashedURLStorage,self).url(name)
        the_hash = self.get_hash(name)
        if "?" in base_url:
            return "%s&%s" % (base_url, the_hash)
        return "%s?%s" % (base_url, the_hash)


class Leg(models.Model):
    date = fields.DateField(default=now)
    name = fields.CharField(max_length=40, unique=True)
    slug = fields.SlugField(max_length=40, db_index=True, editable=False)
    start = fields.CharField(max_length=30)
    end = fields.CharField(max_length=30)
    description = fields.TextField(max_length=320, blank=True)
    duration = fields.DecimalField(decimal_places=1,max_digits=2,default=1.0)
    distanceKM = fields.IntegerField()
    morning = fields.BooleanField(default=True)
    class Meta:
        unique_together = ('date', 'morning')

    def __str__(self):
        return "{} - {} {}: {}km from {} to {}".format(self.name, self.date, "am" if self.morning else "pm", self.distanceKM, self.start, self.end)

    @classmethod
    def Totals(cls):
        return cls.objects.aggregate(distance=Sum('distanceKM'),days=Count('date',distinct=True))
    prepopulated_fields = {"slug": ("title",)}


@receiver(pre_save, sender=Leg)
def set_slug(sender, instance, **kwargs):

    try:
        i = sender.objects.get(pk = instance.pk)
    except ObjectDoesNotExist:
        instance.slug = slugify(instance.start + " " + instance.end)
        return

    # Only set the slug if this instances title/name has changed.
    if i.start == instance.start and i.end == instance.end:
        return

    instance.slug = slugify( instance.start + " " + instance.end )


def get_portrait_path( self, filename):
    """Return the path to the portrait picture for this cyclist
        Note : Because model fields are defined at a class - this cannot be a instance method, and has to be defined
        before the class"""
    return os.path.join('portraits', self.user.username, 'portrait.jpg')

class Cyclist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_index=True)
    legs = models.ManyToManyField( Leg, related_name='cyclist',blank=True)
    targetAmount = fields.DecimalField(max_digits=7, decimal_places=2, default=Decimal(0), blank=False)
    currentPledgedAmount = fields.DecimalField(max_digits=7, decimal_places=2, default=Decimal(0), blank=False)
    fundraising_site = fields.URLField(default='',blank=True)
    statement = fields.TextField(max_length=1200, default="", blank=True)
    picture = models.ImageField(upload_to=get_portrait_path, blank=True,
                                storage=HashedURLStorage()) # Use custom FileStorageSystem as above

    def get_absolute_url(self):
        """Return the absolute URL - always the FundMe page"""
        return reverse('FundMe', kwargs={'username':self.user.username})

    def __repr__(self):
        """A nice representation of this cyclist"""
        return "Cyclist(username={})".format(self.user.username)

    def __str__(self):
        return "Cyclist : {}".format(self.user.username)

    def get_full_name(self):
        """The full name of the cyclist - derived from the User attribute"""
        return self.user.get_full_name()

    def total_distance(self):
        """ Total Distance in km which this cyclist has signed up for"""
        return "{:.1f}".format(sum(l.distanceKM for l in self.legs.all()))

    def total_days(self):
        """ Return the number of days that this cyclist is involved in"""
        return self.legs.all().aggregate(day_count=Count('date', distinct=True))['day_count']

    def percentage_funding(self):
        """Return as a formatted string the % funding - current vs target"""
        if not(self.currentPledgedAmount and self.targetAmount):
            return 0

        if self.targetAmount == 0:
            return 0

        return "{:.0f}".format(100.0 *int(self.currentPledgedAmount)/int(self.targetAmount))

    def fundraising_domain(self):
        """Return as a domain name of the users fundraising site"""
        parsed_uri = urlparse( self.fundraising_site)
        return parsed_uri.netloc

    @classmethod
    def total_funds(cls):
        """Calculate the funds across all cyclists"""
        return cls.objects.aggregate(pledges=Sum('currentPledgedAmount'),target=Sum('targetAmount'))


