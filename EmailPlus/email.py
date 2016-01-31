#!/usr/bin/env python
"""
# SuffolkCycle : Implementation of email.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""
from datetime import timedelta

from django.core.mail import send_mail
from django.conf import settings
from models import EmailQueue
from django.utils.timezone import now
import scheduler

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '06 Jan 2016'


# TODO Support for BCC
# TODO Support for other email arguments

class Email(object):
    def __init__(self, subject, body):
        self._body = body
        self._subject = subject

    def send(self, destination_email):
        """ Try to send the email immediately if we are able"""
        if (scheduler._scheduler_inst is None) or (scheduler._scheduler_inst.immediate_dispatch()):
            send_mail(subject=self._subject,
                      from_email=settings.DEFAULT_FROM_EMAIL,
                      recipient_list=[destination_email, settings.DEFAULT_FROM_EMAIL],
                      message=self._body)
            # Even if we can send immediately - we still need to record so that the volume sent is recorded.
            if scheduler._scheduler_inst is not None:
                qe = EmailQueue.objects.create(subject=self._subject, body_text=self._body,
                                               destination=destination_email,
                                               sent=True, sent_time=now(), queue_time=now())
        else:
            qe = EmailQueue.objects.create(subject=self._subject, body_text=self._body, destination=destination_email,
                                           sent=False, queue_time=now())
