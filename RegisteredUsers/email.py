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
from enum import Enum
from collections import Callable
from django.contrib.auth.models import User

class EmailTypes(Enum):
    NewUserConfirmation = ()
    PasswordChangeWarning = ()
    EmailChangeWarning = ()


from django.core.mail import send_mail

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '06 Jan 2016'


class Email(object):
    _email_defs = { EmailTypes.NewUserConfirmation :
                       { "body":
"""{name},
       Welcome to The Great Suffolk Cycle Ride. Thank you for registering with our website with a username of {username}.
       You can now sign in using the username and password you have provided, and be able to sign up to participate
       in the various cycle ride legs, or to support the cyclists at the various venues and routes.

       We hope you find everything you need on the website - if something is missing, please let us know.

       --
       The Suffolk Cycle Ride Organisation team
       suffolkcycleride2016@gmail.com
""",
                        "subject": "The Great Suffolk Cycle Ride: Registration Complete",
                        "fields": {'name': 'get_full_name',
                                   'username': 'username'}
                  }
    }


    def __init__(self, type):
        if type not in Email._email_defs:
            raise ValueError("Unknown email message type  : {}".format(type))
        self._type = type

    def send(self, user):

        assert isinstance(user,User)
        print user

        email_def = Email._email_defs[self._type]
        recipients = [user.email, "suffolkcycleride2016@gmail.com"]

        # fields list is a list of attribute names on the user object some of which might be callable
        fields = dict( [ (key, value if not isinstance(value,Callable) else value()) for key, value in
                          [(k, user.__getattribute__(v)) for k,v in email_def['fields'].iteritems()] ])

        body_text = email_def["body"].format(**fields)

        send_mail( subject= email_def["subject"],
                      from_email="suffolkcycleride2016@gmail.com",
                      recipient_list=recipients,
                      message= body_text )