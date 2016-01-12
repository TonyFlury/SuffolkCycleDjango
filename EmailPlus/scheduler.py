#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of scheduler

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '11 Jan 2016'

from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from models import EmailQueue
from django.utils.timezone import now
import logging
from threading import Timer

# TODO Deferred rendering ?
# TODO Support for email priority
# TODO Callbacks ?

_scheduler_inst = None


def start_scheduler():
    global _scheduler_inst

    try:
        email_limit = settings.EMAIL_VOLUME_LIMIT
        limit_period = settings.EMAIL_LIMIT_PERIOD
    except AttributeError:
        print "Scheduler not required"
        return

    print "Starting Scheduler"
    _scheduler_inst = EmailScheduler()


class EmailScheduler(object):
    def __init__(self):

        try:
            self.email_limit = settings.EMAIL_VOLUME_LIMIT
        except AttributeError:
            self.email_limit = None

        try:
            self.limit_period = settings.EMAIL_LIMIT_PERIOD
        except AttributeError:
            self.limit_period = None

        try:
            self.timer_period = settings.EMAIL_SCHEDULER_PERIOD
        except AttributeError:
            self.timer_period = 600

        if self.email_limit is None or self.limit_period is None:
            logging.info("Email Scheduler not started")
            return

        self._timer = Timer(self.timer_period, self.schedule)
        self._timer.start()

        print "[{}] started - period {}".format(now(), self.timer_period)
        logging.info("Started Email Scheduler")

    def immediate_dispatch(self):
        """Helper method to see if an email can be sent immediately - or whether it should be queued

          An email can be dispatched immediatley if both the following statements are true.
            a) There are no emails queued which are waiting to be sent.
            b) The # of emails sent in the limit_period does not exceed the limit
        """

        count_sent = EmailQueue.objects.filter(sent=True). \
            filter(sent_time__gte=now() - timedelta(seconds=self.limit_period)).count()

        waiting = EmailQueue.objects.filter(sent=False).count()

        return (count_sent < self.email_limit) and (waiting == 0)

    def schedule(self):
        logging.info("Running email de-queuer")

        # Get number sent in the previous EMAIL_LIMIT_PERIOD
        # First - for simplicity delete all sent records where sent_time >= EMAIL_LIMIT_PERIOD
        EmailQueue.objects.filter(sent=True). \
            filter(sent_time__lte=now() - timedelta(seconds=self.limit_period)).delete()

        # Count emails that have been sent already in the last period
        # Need to filter on time - just in case
        count_sent = EmailQueue.objects.filter(sent=True). \
            filter(sent_time__gte=now() - timedelta(seconds=self.limit_period)).count()

        waiting = EmailQueue.objects.filter(sent=False)

        # Quota is number remaining that can be sent within the EMAIL_LIMIT_PERIOD
        quota = self.email_limit - count_sent

        # Send them one by one
        sent = 0
        for m in waiting:
            send_mail(subject=m.subject,
                      from_email="suffolkcycleride2016@gmail.com",
                      recipient_list=[m.destination, "suffolkcycleride2016@gmail.com"],
                      message=m.body_text)
            m.sent = True
            m.send_time = now()
            m.save()
            sent += 1
            if sent >= quota:
                break

        self._timer = Timer(self.timer_period, self.schedule)
        self._timer.start()

        print "{} De-queuer sent {}".format(now(), sent)
        logging.info("Email de-queuer : sent {} emails".format(sent))
