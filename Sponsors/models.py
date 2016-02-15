from __future__ import unicode_literals

from django.db import models
from markitup.fields import MarkupField
from django.core.validators import RegexValidator


class Opportunity(models.Model):
    class Meta:
        verbose_name = "Opportunity"
        verbose_name_plural = 'Opportunities'

    name = models.CharField(max_length=120, default='', blank=False)
    slug = models.SlugField(default='')
    description = MarkupField(blank=False)
    max_value = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True, default=None)
    value = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True, default=None)
    available = models.BooleanField(default=True)
    taken = models.BooleanField(default=False)

    def __str__(self):
        return "Opportunity : {}".format(self.name)

class Sponsor(models.Model):
    telephone_regex = RegexValidator(regex=r'\d{11}',
                                message='Full phone number must be entered - 11 digits only, no spaces or punctuation.')
    mobile_regex = RegexValidator(regex=r'\d{11}',
                                message='Phone number must be entered in digits only - 11 digits only, no spaces.')
    name = models.CharField(max_length=120, blank=False, default='')
    slug = models.SlugField(default='')
    website = models.URLField(blank=True)
    logo_url = models.URLField()
    potential = models.BooleanField(default=True)
    supports = models.ManyToManyField(to=Opportunity,related_name="supported_by")
    potentials = models.ManyToManyField(to=Opportunity,related_name="potentially_supported_by")
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

    def __str__(self):
            return "Sponsor : {}".format(self.name)