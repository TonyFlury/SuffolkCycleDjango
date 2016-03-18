from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from markitup.fields import MarkupField
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.utils.text import slugify

import os

class Opportunity(models.Model):
    # noinspection PyClassicStyleClass
    class Meta:
        verbose_name = "Opportunity"
        verbose_name_plural = 'Opportunities'

    name = models.CharField(max_length=120, blank=False)
    slug = models.SlugField(default='')
    description = MarkupField(blank=False)
    max_value = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True, default=None)
    value = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True, default=None)
    available = models.BooleanField(default=True)
    taken = models.BooleanField(default=False)

    def __str__(self):
        return "Opportunity : {}".format(self.name)


def get_logo_upload_path( self, filename):
    """Return the path to the portrait picture for this cyclist
        Note : Because model fields are defined at a class - this cannot be a instance method, and has to be defined
        before the class"""
    return os.path.join('sponsors-logos', self.slug, filename)


class Sponsor(models.Model):
    telephone_regex = RegexValidator(regex=r'\d{11}',
                                message='Full phone number must be entered - 11 digits only, no spaces or punctuation.')
    mobile_regex = RegexValidator(regex=r'\d{11}',
                                message='Mobile number must be entered in digits only - 11 digits only, no spaces.')
    contact_name = models.CharField(max_length=120, blank=True)
    slug = models.SlugField(default='')
    company_name = models.CharField(max_length=120, blank=True)
    website = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)
    upload_logo = models.ImageField(upload_to=get_logo_upload_path, blank=True)
    potential = models.BooleanField(default=True, verbose_name="Potential Sponsor only")
    supports = models.ManyToManyField(to=Opportunity,related_name="supported_by", blank=True)
    potentials = models.ManyToManyField(to=Opportunity,related_name="potentially_supported_by", blank=True)
    email = models.EmailField( blank=True)
    telephone = models.CharField( validators=[telephone_regex], blank=True, max_length=11,
                                  help_text='Telephone number - 11 digits only - no spaces or punctuation' )
    mobile = models.CharField( validators=[mobile_regex], blank=True, max_length=11,
                                  help_text='Mobile number - 11 digits only - no spaces or punctuation' )
    communication_preference = models.CharField(max_length=10,
                                                default='email',
                                                choices=[('email','email'),
                                                         ('telephone', 'telephone'),
                                                         ('mobile', 'mobile')])
    accolade = models.TextField(blank=True,help_text="The Accolade for this sponsor once the sponsorship is agreed")

    def __str__(self):
            return "Sponsor : {}".format(self.company_name or self.contact_name)


@receiver(pre_save, sender=Sponsor)
def set_Sponsor_slug(sender, instance, **kwargs):
    name = instance.company_name or instance.contact_name
    instance.slug = slugify(name)


@receiver(pre_save, sender=Opportunity)
def set_opportunity_slug(sender, instance, **kwargs):
    instance.slug = slugify(instance.name)
