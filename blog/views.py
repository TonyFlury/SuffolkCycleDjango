from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.db.models import Q, F, Count, Case, When, Avg, StdDev, Value, CharField
from aggregates import StdDev
import calendar
from collections import Counter
from math import sqrt


# Create your views here.

import models


class BlogMixin(object):

    def get_archive(self, request, display_year=None, display_month=None):
        """ Generate a structured list which described the calendarised archive

            This has to :
                Have a list of years to display and within each list, have a list of months
                Indicate whch year and which month should be displayed initially
                                        (based on which entry is being displayed -if any)

                Note : It might be possible to refactor this so that the raw data is passed to the template and
                using regroup etc the template displays the data, but this works - and there is no compelling reason
                to change this.

            :param request : The WSGI request which triggers this archive display, used to identify if draft documents should be displayed.
            :param display_year : The year (integer or None) which should be opened by default when this archive is displayed
            :param display_month : The month (integer or None) which should be opened by default when this archive is displayed
        """

        if not request.user.is_anonymous():
            archive = models.Entry.objects.filter( Q(is_published = True) | Q( is_published=False, author = request.user )).order_by("-pub_date")
        else:
            archive = models.Entry.objects.filter(is_published = True).order_by("-pub_date")

        # Use year and month arguments to identify which entry in the Archive to display
        # If neither is set - ensure that the year/month with the latest entry is used.
        # If year is set and month is not - ensure that the latest entry in that year is used
        if display_year is None and display_month is None:
            display_year, display_month = archive[0].pub_date.year, archive[0].pub_date.month
        elif display_year is not None and display_month is None:
            qs = archive.filter(pub_date__year = display_year).order_by("-pub_date")
            display_month = qs[0].pub_date.month

        # Construct the archive list in date order.
        # The archive is sent to the template as a list of dictionaries, one dictionary per year
        # Within each year,  the months are a list of dictionaries, one dictionary per month.
        # Within each month, the entries are presented as a list of Entry Instances
        # This nested structure year -> months -> Entries makes display of Archive simple - a set of nested lists.
        organised_archive = []
        this_year, this_month = None, None # Use silly data to start to keep track of new years and months
        for entry in archive:
            # Has the year changed ? If so, buid a new year dictionary.
            if entry.pub_date.year != this_year:
                this_year = entry.pub_date.year
                organised_archive.append({'name':this_year,
                                          'content':[],
                                          'url':reverse('blog:Archive', kwargs={'year':'{:4d}'.format(this_year)} ),
                                          'visible': (this_year == display_year),})
                year_archive = organised_archive[-1]['content']
                # Use an invalid month number so we always build at least one month entry.
                this_month = None

            # Has the month changed ? If so, build a new month dictionary.
            if entry.pub_date.month != this_month:
                this_month = entry.pub_date.month
                year_archive.append( {'name':calendar.month_name[this_month],
                                      'number': "{:02d}".format(this_month), 'content':[],
                                      'url':reverse('blog:Archive',
                                                    kwargs={'year':'{:4d}'.format(entry.pub_date.year),
                                                            'month':'{:02d}'.format(entry.pub_date.month) } ),
                                      'visible': (this_year == display_year) and (this_month == display_month),
                                      })
                month_archive = year_archive[-1]['content']

            month_archive.append(entry)

        return organised_archive

    def get_tag_cloud(self):
        """ Fetch the tag cloud data - categorise the Tags as upper, Average or lower
            Categorisation based on whether they are above or below average (mean)
            Maybe better to use MODE - i.e. the most frequent count.
            Using mode ensures that the largest number of labels are in the 'average' category
        """
        data = models.Tag.objects.\
            annotate(num_entries = Count('entries')).\
            filter(num_entries__gt = 0).aggregate(mean=Avg('num_entries'), std_dev=StdDev('num_entries'))

        mean, std_dev = data['mean'], data['std_dev']

        counts = models.Tag.objects.\
            annotate(num_entries = Count('entries')).\
            filter(num_entries__gt = 0).values_list('num_entries')
        mode = Counter([f[0] for f in counts]).most_common(1)[0][0]

        # Fetch all the relevant tags, filtering out Tags with no entries,
        # and recording categories based on the Average & std_dev
        # Scope for category above upper (mean + 2*std_dev) etc
        return models.Tag.objects.\
                    annotate(num_entries = Count('entries')).\
                    filter(num_entries__gt = 0).\
                    annotate(average=Avg('entries')).\
                    annotate(category=Case(
                                When(num_entries__gt = mean+std_dev, then=Value('upper')),
                                When(num_entries__lt = mean-std_dev, then=Value('lower')),
                                default=Value('avg'),
                                output_field = CharField() ) )

class Main(BlogMixin,View):
    template = "blog/entry_list.html"
    pagination = 2              # Number normally allowed per page
    pagination_orphans = 1      # Minimum allowed per page

    def get(self, request, page=0, tag_slug=None, year=None, month=None, day=None):

        page = int(page) if page else 0

        qs = models.Entry.objects.all()

        query_args = {}
        url_args = {}
        page_args = {}

        name = "blog:Archive" if (year,month,day) != (None,None,None) else ("blog:Search" if tag_slug else 'blog:Main' )

        if tag_slug:
            query_args = {'tags__slug': tag_slug}
            url_args = {'tag_slug': tag_slug}
            page_args = {'tag': models.Tag.objects.get(slug=tag_slug)}
        else:
            if year:
                query_args['pub_date__year']=year
                url_args['year'] = year
                page_args['year'] = year
                if month :
                    query_args['pub_date__month']=month
                    url_args['month'] = month
                    page_args['month'] = month
                    page_args['month_name'] = calendar.month_name[int(month)]
                    if day :
                        query_args['pub_date__day']=day
                        url_args['day'] = day
                        page_args['day'] = day

        qs = qs.filter(**query_args)

        if not request.user.is_anonymous():
            qs = qs.filter( Q(is_published = True) | Q( is_published=False, author = request.user ))
        else:
            qs = qs.filter( is_published = True )

        qs = qs.order_by( "is_published", "-pub_date")

        total = qs.count()

        start_elem = page*self.pagination
        qs = qs[start_elem:]

        remaining = qs.count() # Count from the start of this page to the end of the list

        if remaining >= (self.pagination + self.pagination_orphans):
            qs = qs[:start_elem + self.pagination]
            next_page = True
        else:
            next_page = False

        next_url = reverse(name, kwargs=dict([('page', str(page+1))], **url_args) ) if next_page else None
        prev_url = reverse(name, kwargs=dict([('page', str(page-1))], **url_args) ) if page > 0 else None

        pages, orphans = divmod(page, self.pagination)

        page_args['page'] = page
        page_args['num_pages'] = pages if orphans < self.pagination_orphans else pages +1

        return render(request,self.template, context={
                                    'entries': qs,
                                    'archive': self.get_archive(request, int(year) if year else None, int(month) if month else None ),
                                    'tags': self.get_tag_cloud(),
                                    'next_url': next_url,
                                    'prev_url': prev_url,
                                    'args': page_args })


class Detail(BlogMixin,View):

    template = "blog/entry_detail.html"

    def get(self, request, slug):

        name = "blog:Detail"

        entry = models.Entry.objects.get(slug = slug)

        return render(request,self.template, context={
                                    'entry': entry,
                                    'archive': self.get_archive(request, entry.pub_date.year,entry.pub_date.month),
                                    'tags': self.get_tag_cloud(),
                                    'next_url': None,
                                    'prev_url': None })
