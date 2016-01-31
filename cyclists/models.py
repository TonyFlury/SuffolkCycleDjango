from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Leg(models.Model):
    date = models.DateField(default=now)
    name = models.CharField(max_length=10)
    start = models.CharField(max_length=30)
    end = models.CharField(max_length=30)
    description = models.TextField(max_length=320)
    distanceKM = models.IntegerField()

    def __str__(self):
        return "{} : {}".format(self.name, self.date)

class Cyclist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE )
    legs = models.ManyToManyField( Leg, related_name='cyclist')
    expectedAmount = models.DecimalField(max_digits=7, decimal_places=2, default=0)


