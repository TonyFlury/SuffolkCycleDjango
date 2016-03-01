# coding=utf-8
from __future__ import unicode_literals
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models import fields
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.urlresolvers import reverse

from django.db.models.aggregates import Sum
from django.db.models import F

from collections import Counter
from urlparse import urlparse

import os.path


class OverwriteStorage(FileSystemStorage):
    """Simple extended FileSystemStorage class used for portrait pictures, to ensure only one is stored"""
    def get_available_name(self, name):
        self.delete(name)
        return name


class Leg(models.Model):
    date = fields.DateField(default=now)
    name = fields.CharField(max_length=10, unique=True)
    start = fields.CharField(max_length=30)
    end = fields.CharField(max_length=30)
    description = fields.TextField(max_length=320, blank=True)
    duration = fields.DecimalField(decimal_places=1,max_digits=2,default=1.0)
    distanceKM = fields.IntegerField()

    def __str__(self):
        return "{} : {}".format(self.name, self.date)

def get_portrait_path( instance, filename):
    return os.path.join('portraits', instance.user.username, 'portrait.jpg')

class Cyclist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE )
    legs = models.ManyToManyField( Leg, related_name='cyclist')
    targetAmount = fields.DecimalField(max_digits=7, decimal_places=2, default=0)
    currentPledgedAmount = fields.DecimalField(max_digits=7, decimal_places=2, default=0)
    fundraising_site = fields.URLField(default='',blank=True)
    statement = fields.TextField(max_length=1200, default="", blank=True)
    picture = models.ImageField( upload_to=get_portrait_path, blank=True,
                                 storage=OverwriteStorage() ) # Use custom FileStorageSystem as above

    def get_absolute_url(self):
        return reverse('FundMe', kwargs={'username':self.user.username})

    def __repr__(self):
        return "Cyclist(username={})".format(self.user.username)

    def get_full_name(self):
        return self.user.get_full_name()

    def total_distance(self):
        return sum(l.distanceKM for l in self.legs.all())

    def total_distance_km(self):
        return "{:.1f}".format(self.total_distance())

    def total_distance_miles(self):
        return "{:.1f}".format(self.total_distance() * 0.6214)

    def total_days(self):
        return len(Counter(self.legs.all().values_list('date')))

    def percentage_funding(self):
        return "{:.0f}".format(100.0 *int(self.currentPledgedAmount)/int(self.targetAmount))

    def fundraising_domain(self):
        parsed_uri = urlparse( self.fundraising_site)
        return parsed_uri.netloc

    @classmethod
    def total_funds(cls):
        return cls.objects.aggregate(pledges=Sum('currentPledgedAmount'),target=Sum('targetAmount'))