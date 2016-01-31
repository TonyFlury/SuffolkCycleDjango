from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.db.models import Q, Count, Case, When, Avg, Value, CharField


# Create your views here.

import models

class Main(View):
    template = "blog/entry_list.html"
    pagination = 10             # Number allowed per page
    pagination_orphans = 5      # Minimum allowed per page

    def get(self, request, page=0, tag_slug=None, year=None, month=None, day=None):

        page = page if page else 0

        qs = models.Entry.objects.all()

        if tag_slug:
            qs = qs.filter(tags__pk = tag_slug)
            name = "blog:Search"
        else:
            if year:
                qs = qs.filter(pub_date__year = year)
                if month :
                    qs = qs.filter(pub_date__month = month)
                    if day :
                        qs = qs.filter(pub_date__day = day)
            name = "blog:Archive"

        if not request.user.is_anonymous():
            qs = qs.filter( Q(is_published = True) | Q( is_published=False, author = request.user ))
        else:
            qs = qs.filter( is_published = True )

        start_elem = page*self.pagination
        qs = qs[start_elem:]

        remaining = qs.count()
        if remaining > (self.pagination + self.pagination_orphans):
            qs = qs[:self.pagination]
            next_page = True
        else:
            next_page = False

        if name == "blog:Search":
            next_url = reverse(name, kwargs={'tag_slug':tag_slug, 'page': page + 1}  if next_page else {'tag_slug': tag_slug})
            prev_url = reverse(name, kwargs={'tag_slug':tag_slug, 'page': page - 1} if page > 0 else {'tag_slug', tag_slug})

        if name == "blog:Archive":
            kwargs = {'year': year}
            if month:
                kwargs['month'] = month
            if day:
                kwargs['day'] = day

            next_url = reverse(name, kwargs=dict([('page', page+1)], **kwargs) ) if next_page else None
            prev_url = reverse(name, kwargs=dict([('page', page-1)], **kwargs) ) if page > 0 else None

        qs = qs.order_by( "is_published", "-pub_date")

        if not request.user.is_anonymous():
            archive = models.Entry.objects.filter( Q(is_published = True) | Q( is_published=False, author = request.user )).order_by("-pub_date")
        else:
            archive = models.Entry.objects.filter(is_published = True).order_by("-pub_date")

        #get tags
        tags = models.Tag.objects.annotate(num_entries = Count('entries')).filter(num_entries__gt = 0)

        print [(t.name, t.num_entries) for t in tags]

        average = int(tags.aggregate(Avg('num_entries'))['num_entries__avg'])
        print "Average reference Count {}".format(average)

        tags = tags.annotate(category=Case(
                                When(num_entries__gt = average, then=Value('upper')),
                                When(num_entries = average, then=Value('avg')),
                                When(num_entries__lt = average, then=Value('lower')),
                                default=Value('avg'),
                                output_field = CharField() ) )

        print [(t.name, t.num_entries, t.category) for t in tags]

        return render(request,self.template, context={
                                    'entries': qs,
                                    'archive': archive,
                                    'tags': tags })


class Detail(View):
    pass