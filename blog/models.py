from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.timezone import now
import django.contrib.auth.models
from markitup.fields import MarkupField

from django.dispatch import receiver
from django.db.models.signals import m2m_changed, pre_save
from django.db.models import Count

from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=20, blank=False)
    slug = models.SlugField(max_length=20, db_index=True, editable=False)
    is_permanent = models.BooleanField(default=False, null=False)
    description = models.TextField(null=True)

    def __str__(self):
        """Human readable name"""
        return self.name


    def get_absolute_url(self):
        """ Generate An Absolute URL for this tag"""
        return reverse("blog:Search", kwargs={'tag_slug': self.slug})

    def ref_count(self, distinct=True):
        """Return a reference count for this tag : How many entries use this tag"""
        return self.entries.distinct().count() if distinct else self.entries.count()


class Entry(models.Model):
    title = models.CharField(max_length=60, null=False, blank=False)
    slug = models.SlugField(max_length=60, default="", editable=False, db_index=True)
    pub_date = models.DateField(default=now, db_index=True)
    content = MarkupField(default="", null=False)
    tags = models.ManyToManyField(to=Tag, related_name='entries')
    author = models.ForeignKey(django.contrib.auth.models.User, db_index=True, null=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

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


@receiver(pre_save, sender=Tag)
@receiver(pre_save, sender=Entry)
def set_slug(sender, instance, **kwargs):

    key = 'name' if sender == Tag else 'title'


    try:
        i = sender.objects.get(pk = instance.pk)
    except ObjectDoesNotExist:
        instance.slug = slugify(getattr(instance,key))
        return

    # Only set the slug if this instances title/name has changed.
    if getattr(i, key) == getattr(instance, key):
        return

    instance.slug = slugify( getattr(instance, key) )


@receiver(m2m_changed, sender=Entry.tags.through)
def clear_up(sender, action, **kwargs):
    if (kwargs['model'] != Tag) or (action != 'post_remove') or (sender != Entry.tags.through) or (kwargs['reverse']):
        return

    # Delete all temporary tags in the affected set which is temporary (is_permanent = False), and ref_count = 0
    qs = Tag.objects.filter(pk__in=kwargs['pk_set'], is_permanent=False). \
        annotate(ref_count=Count('entries')). \
        filter(ref_count=0).delete()
