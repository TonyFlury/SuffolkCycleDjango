from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Leg(models.Model):
    name = models.CharField(max_length=10)
    start = models.CharField(max_length=30)
    end = models.CharField(max_length=30)
    description = models.TextField(max_length=320)
    distanceKM = models.IntegerField()

class Cyclist(models.Model):
    user = models.ForeignKey(to=User)
    hometown = models.CharField(max_length=50)
    legs = models.ManyToManyField( Leg )
    expectedAmount = models.DecimalField(max_digits=5, decimal_places=2)



