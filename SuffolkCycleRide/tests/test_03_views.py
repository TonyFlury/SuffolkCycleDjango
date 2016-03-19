#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of test_03_views.py

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
__created__ = '19 Feb 2016'

from django.conf import settings

from django.test import TestCase
from django.test import Client
from django.core import mail
from django.contrib.auth.models import User

from django.core.urlresolvers import reverse

from SuffolkCycleRide import views
from stats.models import PageVisit

from django.utils.timezone import now
from datetime import timedelta, date

import SuffolkCycleRide.forms as forms

import newsletter.models
import newsletter.forms

import RegisteredUsers.forms
import cyclists.models

from bs4 import BeautifulSoup

from SuffolkCycleRide.tests import TestCase

class StaticUrls(TestCase):
    def setUp(self):
        self.client = Client()
        pass

    def tearDown(self):
        pass

    def test_010_homepage(self):
        ts = now()
        r = self.client.get(reverse('Home'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.home.__name__)
        self.assertEqual(r.templates[0].name, 'SuffolkCycleRide/pages/home.html')
        self.assertAlmostEqual(PageVisit.most_recent('Home').timestamp, ts, delta=timedelta(milliseconds=500))

    def test_012_privacy(self):
        ts = now()
        r = self.client.get(reverse('Privacy'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.privacy.__name__)
        self.assertEqual(r.templates[0].name, 'SuffolkCycleRide/pages/privacy.html')
        self.assertAlmostEqual(PageVisit.most_recent('Privacy').timestamp, ts, delta=timedelta(milliseconds=500))


class GetInvolved(TestCase):
    def setUp(self):
        self.client = Client()
        pass

    def tearDown(self):
        pass

    def test_010_GetInvolvedGet(self):
        ts = now()
        r = self.client.get(reverse('GetInvolved'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.GetInvolved.as_view().__name__)
        self.assertEqual(r.templates[0].name, 'base/VerticalForm.html')
        # Issue 19 - Temporarily Disable Newsletter Capability
        # self.assertIsInstance(r.context[-1]['forms'][0]['form'], newsletter.forms.NewsletterSignUpForm)
        self.assertIsInstance(r.context[-1]['forms'][0]['form'], RegisteredUsers.forms.NewUserForm)
        self.assertAlmostEqual(PageVisit.most_recent('GetInvolved').timestamp, ts, delta=timedelta(milliseconds=100))

    def test_011_GetInvolvedPostNewsLetter(self):
        """Check that a correctly completed Newsletter Signup form results in correct templates and a new instance"""

        self.skipTest('Issue 19 - Newsletter Capability Temporarily Disable')
        # Todo - Need to test the Newsletter Signup Form for incorrect/blank entries.
        ts = now()
        
        # On a view with multiple submits - we need to be explicit about which one is being clicked
        r = self.client.post(reverse('GetInvolved'), data={'nl-email':'tester@test.com',
                                                           'submit':u'Send me the newsletter'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.GetInvolved.as_view().__name__)
        self.assertTemplateUsed(r, 'newsletter/pages/subscription_confirmation.html')

        # Check we now have a newsletter entry
        nl = newsletter.models.NewsletterRecipient.objects.all()
        self.assertEqual(len(nl),1)
        self.assertEqual(nl[0].email, 'tester@test.com')

    def test_012_GetInvolvedPostSignUp(self):
        ts = now()
        r = self.client.post(reverse('GetInvolved'), data={'r-first_name':'Tester',
                                                           'r-last_name':'Testertestington',
                                                           'r-email':'Tester@test.com',
                                                           'r-username':'tester',
                                                           'r-password':'testtesttest',
                                                           'r-confirm_password':'testtesttest',
                                                           'submit':u'Register'})
        self.assertEqual(r.resolver_match.func.__name__, views.GetInvolved.as_view().__name__)
        self.assertRedirects(r, reverse('Dashboard:Home'))

        # Check User is created
        user = User.objects.get(username='tester')
        self.assertEqual(user.email, 'Tester@test.com')

        # Check the user has been signed in
        self.assertTrue('_auth_user_id' in self.client.session)

        # Confirm email has been sent to user with username and reset url
        message = mail.outbox[-1]
        self.assertTrue('Tester@test.com' in message.to )
        self.assertIn( 'tester', message.body )
        self.assertIn( 'http://testserver{}'.format( reverse("User:ResetRequest") ), message.body)

class ContactUs(TestCase):
    def setUp(self):
        self.client = Client()
        pass

    def tearDown(self):
        pass

    def test_010_ContactUsGet(self):
        ts = now()
        r = self.client.get(reverse('ContactUs'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.ContactUs.as_view().__name__)
        self.assertEqual(r.templates[0].name, 'base/SingleForm.html')
        self.assertAlmostEqual(PageVisit.most_recent('ContactUs').timestamp, ts, delta=timedelta(milliseconds=100))

    def test_011_ContactUsPost(self):
        email, name, reason, content = 'test.test@tester.com','Tester Testing','volunteering','This is a test message'
        r = self.client.post(reverse('ContactUs'),
                             data = {'sender_email':email,
                                     'sender_name': name,
                                     'reason':reason,
                                     'content':content})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.ContactUs.as_view().__name__)
        self.assertTemplateUsed(r, 'base/SingleForm.html')

        # Fetch emails
        self.assertEqual(len(mail.outbox),2)
        user_message = mail.outbox[-1]
        staff_message = mail.outbox[-2]

        # Check message sent to staff
        self.assertIn(reason, staff_message.subject)
        self.assertIn(name, staff_message.subject)
        self.assertEqual(settings.DEFAULT_FROM_EMAIL, staff_message.from_email)
        self.assertEqual(staff_message.to, [settings.DEFAULT_TO_EMAIL])
        self.assertIn(email, staff_message.body)
        self.assertIn(name, staff_message.body)
        self.assertIn(content, staff_message.body)

        # Check message sent to user
        self.assertEqual(settings.DEFAULT_FROM_EMAIL, user_message.from_email)
        self.assertEqual(user_message.to, [email])
        self.assertIn(forms.ContactChoices.fullVersion(reason), user_message.body)
        self.assertIn(name, user_message.body)
        self.assertIn(email, user_message.body)
        self.assertIn(content, user_message.body)

class FundMe(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user( first_name='Chester', last_name="Tester",
                                               username='Tester', email='tester@test.com',
                                               password='testtest')
        self.cyclist = cyclists.models.Cyclist.objects.get(user=self.user)
        self.cyclist.targetAmount = 1000
        self.cyclist.currentPledgedAmount = 50
        self.cyclist.save()

    def tearDown(self):
        pass

    def test_BasicAccess(self):
        """Prove that access is available to the FundMe page - even when not logged in"""
        ts = now()
        r = self.client.get( reverse('FundMe', kwargs={'username':self.user.username}))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.fundme.__name__)
        self.assertEqual(r.templates[0].name, 'SuffolkCycleRide/pages/fundme.html')
        self.assertAlmostEqual(PageVisit.most_recent('FundMe', user=self.user).timestamp, ts, delta=timedelta(milliseconds=100))

        self.assertInContext(response=r, attr_name='cyclist', expected=self.cyclist)
        self.assertNotInContext(response=r, attr_name='mockup')

        # Prove that there is no site menu accessible on this page
        self.assertHTMLNotMatchSelector(r.content, 'ul.chevronbar')

class TheEvent(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def create_legs(self):
        self.legs = [ cyclists.models.Leg(date=date(2020,07,10) + timedelta(days=10+c/2),
                            name='Leg{}'.format(c), start='Town{}'.format(c+1), end='Town{}'.format(c+2),
                            morning=c%2==0, distanceKM=17) for c in range(0,6)]
        for l in self.legs:
            l.save()

    def test_001_TestBasicAccess(self):
        ts = now()
        r = self.client.get( reverse('TheEvent'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func, views.the_event)
        self.assertEqual(r.templates[0].name, 'SuffolkCycleRide/pages/theevent.html')
        self.assertAlmostEqual(PageVisit.most_recent('TheEvent').timestamp, ts, delta=timedelta(milliseconds=100))

        # Confirm that no legs are passed to the template
        self.assertInContext(response=r, attr_name = 'event.legs', expected=[])

    def test_002_TestEventList(self):
        self.create_legs()
        ts = now()
        r = self.client.get( reverse('TheEvent'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func, views.the_event)
        self.assertEqual(r.templates[0].name, 'SuffolkCycleRide/pages/theevent.html')
        self.assertAlmostEqual(PageVisit.most_recent('TheEvent').timestamp, ts, delta=timedelta(milliseconds=100))

        # Test that the legs appear in the right order
        self.assertInContext(response=r, attr_name = 'event.legs', expected=self.legs)

        # Test the distance and start/end location appear
        st = BeautifulSoup(r.content, 'html5lib')
        summary = st.select('div.summary')[0].select('p')
        self.assertIn(self.legs[0].start, unicode(summary[0].text))
        self.assertIn(self.legs[-1].end, unicode(summary[0].text))