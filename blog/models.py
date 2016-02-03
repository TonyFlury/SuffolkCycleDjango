from __future__ import unicode_literals

import re

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.timezone import now
import django.contrib.auth.models
from markitup.fields import MarkupField

from django.dispatch import receiver
from django.db.models.signals import m2m_changed, pre_save
from django.db.models import Count

slug_re = re.compile(r'\s')


def slugify(text):
    """ Remove whitespace from the text so it can be used as a slug
    :param text: The text to be slugified - implemented as a compiled re for efficiency
    :return : None
    """
    return (slug_re.sub("_", text)).lower()


# noinspection PyProtectedMember
def validate(model, field, value):
    """Generic basic validation function
    :param model: The Model class being validated
    :param field: The name of the field to be validated
    :param value: The value being set on this field
    :raise ValueError : Raised if any validation test fails
    :return None:
    """
    model_field = model._meta.get_field(field)

    if isinstance(model_field, models.CharField):
        if not model_field.blank and not value:
            raise ValueError('{} name cannot be blank/None'.format(model.__name__))

        if model_field.max_length and (len(value) > model_field.max_length):
            raise ValueError('{} {} too long; cannot be more than {} characters'.format(model.__name__, field,
                                                                                        model_field.max_length))


class Tag(models.Model):
    name = models.CharField(max_length=20, blank=False)
    slug = models.CharField(max_length=20, db_index=True, editable=False)
    is_permanent = models.BooleanField(default=False, null=False)

    @classmethod
    def create(cls, name, is_permanent = False, *args, **kwargs):
        """Override create so that we can slugify the tag name
        :param name: The name for this Tag
        :param is_permanent : Whether this Tag should be deleted if the ref_count drops to zero
        """
        validate(cls, 'name', name)

        tag = cls(name=name, *args, **kwargs)
        tag.slug = slugify(name)

        return tag

    def __str__(self):
        """Human readable name"""
        return self.name

    def save(self, *args, **kwargs):
        """ Re slugify the name when saved """
        validate(self.__class__, 'name', self.name)
        self.slug = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """ Generate An Absolute URL for this tag"""
        return reverse("blog:Search", kwargs={'tag_slug': self.slug})

    def ref_count(self, distinct=True):
        """Return a reference count for this tag : How many entries use this tag"""
        return self.entries.distinct().count() if distinct else self.entries.count()


class Entry(models.Model):
    title = models.CharField(max_length=60, null=False, blank=False)
    slug = models.CharField(max_length=60, default="", editable=False, db_index=True)
    pub_date = models.DateField(default=now, db_index=True)
    content = MarkupField(default="", null=False)
    tags = models.ManyToManyField(to=Tag, related_name='entries')
    author = models.ForeignKey(django.contrib.auth.models.User, db_index=True, null=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @classmethod
    def create(cls, title, **kwargs):
        validate(cls, 'title', title)

        entry = cls(title=title, **kwargs)
        entry.slug = slugify(title)
        return entry

    def save(self, *args, **kwargs):
        """Validate the title of the instance"""
        validate(self.__class__, 'title', self.title)
        super(Entry, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:Detail", kwargs={'slug': self.slug})

    @property
    def tag_text(self):
        """ Tags field as a comma separated set of tags"""
        return ", ".join([t.name for t in self.tags.all()])

    @tag_text.setter
    def tag_text(self, tags):
        """ Enable tags to be set as a comma separated text field """
        proposed = [Tag.objects.get_or_create(name=t.strip())[0] for t in tags.split(',') if t]

        self.tags = proposed

        self.save()

@receiver(pre_save, sender=Entry)
def set_slug(sender, instance, **kwargs):
    if (sender != Entry):
        return

    print "bing"
    try:
        i = Entry.objects.get(pk = instance.pk)
    except ObjectDoesNotExist:
        print "bong"
        instance.slug = slugify(instance.title)
        return

    if i.title == instance.title:
        return

    instance.slug = slugify(instance.title)
    print "bong"

@receiver(m2m_changed, sender=Entry.tags.through)
def clear_up(sender, action, **kwargs):
    if (kwargs['model'] != Tag) or (action != 'post_remove') or (sender != Entry.tags.through) or (kwargs['reverse']):
        return

    # Delete all temporary tags in the affected set which is temporary (is_permanent = False), and ref_count = 0
    qs = Tag.objects.filter(pk__in=kwargs['pk_set'], is_permanent=False). \
        annotate(ref_count=Count('entries')). \
        filter(ref_count=0).delete()
