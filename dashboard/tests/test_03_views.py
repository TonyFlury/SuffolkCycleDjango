#!/usr/bin/env python
# coding=utf-8
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
__created__ = '26 Feb 2016'

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse
from django.utils.timezone import now

from dashboard import forms, models, views
from stats.models import PageVisit
from datetime import date, timedelta

import RegisteredUsers.forms
import RegisteredUsers.models
import cyclists.models

from bs4 import BeautifulSoup

class Dashboard(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user( first_name='Chester', last_name="Tester",
                                               username='Tester', email='tester@test.com',
                                               password='testtest')

    def tearDown(self):
        pass

    def test_010_DashboardNotSignedIn(self):
        """Test that there is no access to the Dashboard when not signed in"""
        r = self.client.get(reverse('Dashboard:Home'))
        self.assertRedirects(r, reverse('GetInvolved'))

    def test_011_DashboardSignedIn(self):
        """Test that a logged in User gets to the Dashboard"""
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:Home'))
        self.assertEqual(r.status_code,200)
        self.assertTemplateUsed(r, "dashboard/pages/dashboard.html")


class MyDetails(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user( first_name='Chester', last_name="Tester",
                                               username='Tester', email='tester@test.com',
                                               password='testtest')

    def tearDown(self):
        pass

    def test_010_MyDetailsNotSignedIn(self):
        """Test that there is no access to the Dashboard when not signed in"""
        r = self.client.get(reverse('Dashboard:MyDetails'))
        self.assertRedirects(r, reverse('GetInvolved'))

    def test_011_MyDetailsSignedIn(self):
        """Test that a logged in User gets to the Dashboard"""
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:MyDetails'))
        self.assertEqual(r.status_code,200)
        self.assertTemplateUsed(r, "dashboard/pages/MyDetails.html")
        self.assertIsInstance(r.context[-1]['form'], forms.MyDetails)
        self.assertEqual(r.context[-1]['form']['email'].value(), self.user.email)

    def test_012_MyDetailsMainSubmit(self):
        """Test that the Details Page gets Posted Correctly - just change the email address for now"""
        ts = now()
        self.client.force_login(user=self.user)
        r = self.client.post(reverse('Dashboard:MyDetails'),
                            data={'email':'tester@test.test.com',
                                  'submit':u'Save' })
        self.assertEqual(r.status_code,200)
        self.assertTemplateUsed(r, "dashboard/pages/MyDetails.html")
        self.assertTrue('confirmation' in r.context[-1])

        # Test that the db has changed
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'tester@test.test.com')

        # Test that the Page Visit has been recorded
        self.assertAlmostEqual(PageVisit.most_recent(document='Details Changed').timestamp, ts,
                               delta=timedelta(milliseconds=500))

    def test_013_MyDetailsChangePasswordSubmit(self):
        """Test that the Details Page gets Posted Correctly"""
        self.client.force_login(user=self.user)
        r = self.client.post(reverse('Dashboard:MyDetails'),
                            data={'submit':u'Change Password' })
        self.assertRedirects(r, reverse('Dashboard:PasswordReset'))

    def test_020_ChangePasswordNotLoggedin(self):
        r = self.client.get(reverse('Dashboard:PasswordReset'))
        self.assertRedirects(r, reverse('GetInvolved'))

    def test_021_ChangePasswordLoggedIn(self):
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:PasswordReset'))
        self.assertTemplateUsed(r, "dashboard/pages/PasswordChange.html")
        self.assertIsInstance(r.context[-1]['form'], RegisteredUsers.forms.PasswordReset)
        self.assertNotEqual(r.context[-1]['form']['uuid'].value(), '')

        # Check that the PasswordResetRequest instance has an expiry of today() + 1
        prr = RegisteredUsers.models.PasswordResetRequest.objects.get(uuid=r.context[-1]['form']['uuid'].value())
        self.assertEqual( prr.expiry-date.today(), timedelta(days=1))
        self.assertEqual( prr.user, self.user)

    def test_022_ChangePasswordSubmit(self):
        """Test that the change Password works correctly"""
        ts = now()

        prr = RegisteredUsers.models.PasswordResetRequest(user=self.user, expiry=date.today()+timedelta(days=1) )
        prr.save()

        self.client.force_login(user=self.user)
        r = self.client.post(reverse('Dashboard:PasswordReset'),
                             data={'uuid':str(prr.uuid), 'newPassword':'test','confirmPassword':'test'})
        self.assertTemplateUsed(r, "dashboard/pages/PasswordChange.html")
        self.assertTrue('confirmation' in r.context[-1])

        # Check that the PasswordResetRequest instance is deleted
        with self.assertRaises(ObjectDoesNotExist):
            RegisteredUsers.models.PasswordResetRequest.objects.get(uuid=prr.uuid)
        self.assertEqual(authenticate(username='Tester',password='test'), self.user)

        # Check the Password change is recorded in the stats
        self.assertAlmostEqual(PageVisit.most_recent(document='Dashboard:PasswordReset', user=self.user).timestamp, ts,
                               delta=timedelta(milliseconds=500))

    # Todo Need Unit Tests to test Portrait upload and deletion

class CycleRoutes(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user( first_name='Chester', last_name="Tester",
                                               username='Tester', email='tester@test.com',
                                               password='testtest')

        # Create and save 3 Legs - date offset of 10 days - so we can tweak the order if neccessary
        self.leg1 = cyclists.models.Leg( date = date.today() + timedelta(days=10),
                                         name = 'Leg1',
                                         start = 'Town1', end='Town2',
                                         distanceKM = 17)
        self.leg1.save()
        self.leg2 = cyclists.models.Leg( date = date.today() + timedelta(days=11),
                                         name = 'Leg2',
                                         start = 'Town2', end='Town3',
                                         distanceKM = 19)
        self.leg2.save()
        self.leg3 = cyclists.models.Leg( date = date.today() + timedelta(days=12),
                                         name = 'Leg3',
                                         start = 'Town3', end='Town4',
                                         distanceKM = 23)
        self.leg3.save()
        self.cyclist = cyclists.models.Cyclist.objects.get(user=self.user)

    def checkbox_status(self, content):
        soup = BeautifulSoup(content, 'html5lib')
        boxes = soup.select("input.checkbox")
        return {box['value']:('checked' in box.attrs) for box in boxes}

    def test_010_CycleRoutesNotSignedIn(self):
        """Test that there is no access to the Dashboard when not signed in"""
        r = self.client.get(reverse('Dashboard:CycleRoutes'))
        self.assertRedirects(r, reverse('GetInvolved'))

    def test_011_CycleRoutesSignedIn(self):
        """Test that a logged in User gets to the Dashboard"""
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:CycleRoutes'))
        self.assertEqual(r.status_code,200)
        self.assertTemplateUsed(r, "dashboard/pages/CycleRoutes.html")

    def test_012_RoutesNotSelected(self):
        """Test that with no routes currently selected - the routes appear in date order"""
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:CycleRoutes'))
        self.assertEqual(r.status_code,200)
        self.assertTemplateUsed(r, "dashboard/pages/CycleRoutes.html")
        self.assertEqual(len(r.context[-1]['legs']), 3)
        self.assertSequenceEqual(r.context[-1]['legs'], [self.leg1, self.leg2, self.leg3])
        self.assertEqual(self.checkbox_status(r.content), {str(self.leg1.pk):False,
                                                           str(self.leg2.pk):False,
                                                           str(self.leg3.pk):False})

    def test_013_RoutesNotSelected(self):
        """Test that with no routes currently selected - the routes appear in date order - modfied date"""
        self.leg2.date = self.leg1.date - timedelta(days=2)
        self.leg2.save()
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:CycleRoutes'))
        self.assertEqual(r.status_code,200)
        self.assertTemplateUsed(r, "dashboard/pages/CycleRoutes.html")
        self.assertEqual(len(r.context[-1]['legs']), 3)
        self.assertSequenceEqual(r.context[-1]['legs'], [self.leg2, self.leg1, self.leg3])
        self.assertEqual(self.checkbox_status(r.content), {str(self.leg1.pk):False,
                                                           str(self.leg2.pk):False,
                                                           str(self.leg3.pk):False})

    def test_020_RoutesSelected(self):
        """Test that with one routes currently selected - the routes appear in order - and the correct one selected"""
        self.cyclist.legs.add(self.leg2)
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:CycleRoutes'))
        self.assertEqual(r.status_code,200)
        self.assertTemplateUsed(r, "dashboard/pages/CycleRoutes.html")
        self.assertEqual(len(r.context[-1]['legs']), 3)
        self.assertSequenceEqual(r.context[-1]['legs'], [self.leg1, self.leg2, self.leg3])
        self.assertEqual(self.checkbox_status(r.content), {str(self.leg1.pk):False,
                                                           str(self.leg2.pk):True,
                                                           str(self.leg3.pk):False})

    def test_021_RoutesSelected2(self):
        """Test that with one routes currently selected - the routes appear in order - and the correct one selected"""
        self.cyclist.legs.add(self.leg2, self.leg3)
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:CycleRoutes'))
        self.assertEqual(r.status_code,200)
        self.assertTemplateUsed(r, "dashboard/pages/CycleRoutes.html")
        self.assertEqual(len(r.context[-1]['legs']), 3)
        self.assertSequenceEqual(r.context[-1]['legs'], [self.leg1, self.leg2, self.leg3])
        self.assertEqual(self.checkbox_status(r.content), {str(self.leg1.pk):False,
                                                           str(self.leg2.pk):True,
                                                           str(self.leg3.pk):True})

    def test_025_SelectRouteandPost(self):
        """Test that a selection of a checkbox is reflected into the database"""
        self.cyclist.legs.add(self.leg2)
        self.client.force_login(user=self.user)
        r=self.client.post(reverse('Dashboard:CycleRoutes'),
                           data={'submit':'Save',
                                 'selected':('2','3')})
        self.assertEqual(r.status_code,200)
        self.assertTemplateUsed(r, "dashboard/pages/CycleRoutes.html")
        self.assertTrue('confirmation' in r.context[-1] )

        self.assertTrue(self.leg1 not in self.cyclist.legs.all())
        self.assertTrue(self.leg2 in self.cyclist.legs.all())
        self.assertTrue(self.leg3 in self.cyclist.legs.all())

class FundRaising(TestCase):
    def setUp(self):
        self.user = User.objects.create_user( first_name='Chester', last_name="Tester",
                                               username='Tester', email='tester@test.com',
                                               password='testtest')
        self.cyclist = cyclists.models.Cyclist.objects.get(user=self.user)

    def tearDown(self):
        pass

    def test_010_FundRaisingNotSignedIn(self):
        """Test that there is no access to the Dashboard when not signed in"""
        r = self.client.get(reverse('Dashboard:FundRaising'))
        self.assertRedirects(r, reverse('GetInvolved'))

    def test_011_FundRaisingSignedIn(self):
        """Test that a logged in User gets to the Dashboard"""
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:FundRaising'))
        self.assertEqual(r.status_code,200)
        self.assertTemplateUsed(r, "dashboard/base/dashboard_form.html")
        self.assertIsInstance(r.context[-1]['form'], forms.FundRaising)
        self.assertEqual(r.context[-1]['form'].instance, self.cyclist)

    def test_012_FundRaisingValuesShown(self):
        """Test that the form is populated correctly"""
        self.cyclist.targetAmount = 500
        self.cyclist.save()
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:FundRaising'))
        self.assertEqual(r.status_code,200)
        self.assertTemplateUsed(r, "dashboard/base/dashboard_form.html")
        self.assertIsInstance(r.context[-1]['form'], forms.FundRaising)
        self.assertEqual(r.context[-1]['form'].instance, self.cyclist)
        self.assertEqual(r.context[-1]['form']['targetAmount'].value(), self.cyclist.targetAmount)
        self.assertContains(r, reverse('FundMe',kwargs={'username':self.user.username}))
