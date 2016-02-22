from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from markitup.fields import MarkupField
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.utils.text import slugify


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


class Sponsor(models.Model):
    telephone_regex = RegexValidator(regex=r'\d{11}',
                                message='Full phone number must be entered - 11 digits only, no spaces or punctuation.')
    mobile_regex = RegexValidator(regex=r'\d{11}',
                                message='Mobile number must be entered in digits only - 11 digits only, no spaces.')
    name = models.CharField(max_length=120, blank=False)
    slug = models.SlugField(default='')
    company_name = models.CharField(max_length=120, blank=True)
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


@receiver(pre_save, sender=Opportunity)
@receiver(pre_save, sender=Sponsor)
def set_slug(sender, instance, **kwargs):

    try:
        i = sender.objects.get(pk = instance.pk)
    except ObjectDoesNotExist:
        instance.slug = slugify(instance.name)
        return

    if i.name == instance.name:
        return

    instance.slug = slugify(instance.name)
