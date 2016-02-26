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
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core import mail
from RegisteredUsers import views, forms, models
from stats.models import PageVisit

from datetime import timedelta, date

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '25 Feb 2016'


class SignIn(TestCase):
    """Test the SignIn View

        Conditions to test
            username & password are mandatory - and must match the details in the db
            Page Visits get recorded on successful Login and logout
            User is logged in on successful Post

        Notes :
            1) Form provides a login method - which is tested here, since the login needs a session on a client
            2) Appropriate errors generated if user is not recognised - tested via the form - see
                    test_02_forms.SignInForm

    """

    def setUp(self):
        self.client = Client()
        self.chester = User.objects.create_user(first_name='Chester',
                                                last_name='Tester',
                                                email='tester@test.com',
                                                username='testertestington',
                                                password='testertester')

    def tearDown(self):
        pass

    def test_010_SignInGet(self):
        """Test that going to the SignIn page returns the right view, template and form"""
        r = self.client.get(reverse('User:SignIn'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.SignIn.as_view().__name__)
        self.assertTemplateUsed(r, 'RegisteredUsers/pages/SignIn.html')
        self.assertIsInstance(r.context[-1]['form'], forms.SignInForm)

    def test_011_SignInPost(self):
        """Test that Posting valid details to the SignIn page results in a correctly logged in user"""
        ts = now()
        r = self.client.post(reverse('User:SignIn'), data={'username': 'testertestington', 'password': 'testertester'})
        self.assertEqual(r.resolver_match.func.__name__, views.SignIn.as_view().__name__)
        self.assertTrue(self.client.session['_auth_user_id'], self.chester.pk)
        self.assertRedirects(r, reverse('Home'))
        self.assertAlmostEqual(PageVisit.most_recent('User:SignIn').timestamp, ts, delta=timedelta(milliseconds=200))


class SignOut(TestCase):
    def setUp(self):
        self.client = Client()
        self.chester = User.objects.create_user(first_name='Chester',
                                                last_name='Tester',
                                                email='tester@test.com',
                                                username='testertestington',
                                                password='testertester')
        self.client.logout()

    def tearDown(self):
        pass

    def test_010_SignOutNotSignedIn(self):
        """Sign Out when no-one is signed in - should not result in an error"""
        ts = now()
        self.assertFalse('_auth_user_id' in self.client.session)
        r = self.client.get(reverse('User:SignOut'))
        self.assertEqual(r.resolver_match.func.__name__, views.SignOut.__name__)
        self.assertRedirects(r, reverse('Home'))
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertTrue(PageVisit.most_recent(document='User:SignOut', user=None) is None)

    def test_011_SignOutOk(self):
        """Sign Out when user is signed in - must result in correct logout"""
        ts = now()
        self.assertTrue(self.client.login(username='testertestington', password='testertester'))
        self.assertTrue(self.client.session['_auth_user_id'], self.chester.pk)
        response = self.client.get(reverse('User:SignOut'))
        self.assertRedirects(response, reverse('Home'))
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertAlmostEqual(PageVisit.most_recent('User:SignOut').timestamp, ts, delta=timedelta(milliseconds=200))


class ResetRequest(TestCase):
    """Test the ResetRequest View

        Conditions to test
            email mandatory - and must match the details in the db
            appropriate email sent on successful Post
            Page Visits get recorded on successful POST
            PassowrdResetRequest model instance created.

        Notes :
    """

    def setUp(self):
        self.client = Client()
        self.chester = User.objects.create_user(first_name='Chester',
                                                last_name='Tester',
                                                email='tester@test.com',
                                                username='testertestington',
                                                password='testertester')

    def tearDown(self):
        pass

    def test_010_ResetRequestGet(self):
        """Get the ResetRequest Page - and prove that the page is serverd on the right template and form"""
        r = self.client.get(reverse('User:ResetRequest'))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'base/SingleForm.html')
        self.assertIsInstance(r.context[-1]['form'], forms.PasswordResetRequest)

    def test_020_ResetRequestPost(self):
        """Complete the ResetRequest Post - and ensure that a PasswordResetRequest Instance is created"""
        r = self.client.post(reverse('User:ResetRequest'), data={'email': 'tester@test.com'})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'RegisteredUsers/pages/ResetConfirmed.html')

        # Confirm that a Password Reset Request is created with the correct expiry date
        prr = models.PasswordResetRequest.objects.filter(user=self.chester)
        self.assertEqual(len(prr), 1)
        prr = prr[0]
        self.assertEqual(prr.expiry, date.today() + timedelta(days=14))

        # Confirm that the reset request confirmation email is sent - with the right URL and expiry date
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        url = "http://{}{}".format('testserver', prr.get_url())
        date_str = prr.expiry.strftime('%B %d, %Y')
        self.assertIn(url, message.body)
        self.assertIn(date_str, message.body)


class Reset(TestCase):
    """ Test the password Reset form
        Conditions to test
            Accesible via a reset request url
            uuid gets added correctly to the form
            Invalid URLs are correctly trapped and errored
            A success post will Delete the prr, and change the password
    """

    # Todo - Refactor to use SingleForm and confirmation popup - rather than custom templates

    def setUp(self):
        self.client = Client()
        self.chester = User.objects.create_user(first_name='Chester',
                                                last_name='Tester',
                                                email='tester@test.com',
                                                username='testertestington',
                                                password='testertester')
        self.prr = models.PasswordResetRequest(user=self.chester,
                                               expiry=date.today() + timedelta(days=14))
        self.prr.save()
        self.expire = models.PasswordResetRequest(user=self.chester,
                                                  expiry=date.today() - timedelta(days=1))
        self.expire.save()

    def tearDown(self):
        pass

    def test_010_ResetGetValid(self):
        """Test that we are able to get the PasswordReset  with a correct uuid"""
        r = self.client.get(reverse('User:Reset', args=[str(self.prr.uuid)]))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'RegisteredUsers/pages/PasswordChange.html')
        self.assertIsInstance(r.context[-1]['form'], forms.PasswordReset)
        self.assertEqual(r.context[-1]['form']['uuid'].value(), str(self.prr.uuid))

    def test_011_ResetGetExpired(self):
        """Test that we are able to get the PasswordReset  with a uuid which we know has expired"""
        r = self.client.get(reverse('User:Reset', args=[str(self.expire.uuid)]))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'RegisteredUsers/pages/UnknownReset.html')

    def test_012_ResetGetInvalid(self):
        """Test that we are able to get the PasswordReset  with a uuid which we know is invalid (too short)"""
        r = self.client.get(reverse('User:Reset', args=[str(self.expire.uuid)[:-2]]))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'RegisteredUsers/pages/UnknownReset.html')

    def test_020_ResetPost(self):
        """Test that we are able to correctly Post a reset - with a new password"""

        # Ensure no-one is logged in currently
        self.assertFalse('_auth_user_id' in self.client.session)

        # Do a password reset
        r = self.client.post(reverse('User:Reset', args=[str(self.prr.uuid)]),
                             data={'uuid': str(self.prr.uuid),
                                   'newPassword': 'test',
                                   'confirmPassword': 'test'})
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'RegisteredUsers/pages/PasswordChange.html')
        self.assertEqual(r.context[-1]['confirmation'], True)

        # Confirm that the user is now logged in
        self.assertTrue(self.client.session['_auth_user_id'], self.chester.pk)

        # Confirm password has actually been changed - i.e. can we authenticate with the new password
        self.assertEqual(authenticate(username=self.chester.username, password='test'), self.chester)