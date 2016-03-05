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
import os.path
import shutil

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse
from django.utils.timezone import now

from dashboard import forms, views
from stats.models import PageVisit
from datetime import date, timedelta

import RegisteredUsers.forms
import RegisteredUsers.models
import cyclists.models

from django.core.files.uploadedfile import SimpleUploadedFile
from StringIO import StringIO

from bs4 import BeautifulSoup

from PIL import Image

from TempDirectoryContext import TempDirectoryContext as TDC

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '26 Feb 2016'


class Dashboard(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(first_name='Chester', last_name="Tester",
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
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "dashboard/pages/dashboard.html")
        self.assertEqual(r.resolver_match.func.__name__, views.UserDashboard.__name__)


class MyDetails(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(first_name='Chester', last_name="Tester",
                                             username='Tester', email='tester@test.com',
                                             password='testtest')
        self.cyclist = cyclists.models.Cyclist.objects.get(user = self.user)

    def tearDown(self):
        if os.path.exists(os.path.join( settings.MEDIA_ROOT,
                                        self.user.username,
                                        'portrait')):
            shutil.rmtree(os.path.join( settings.MEDIA_ROOT,
                                        self.user.username,
                                        'portrait') )
        pass

    def test_010_MyDetailsNotSignedIn(self):
        """Test that there is no access to the Dashboard when not signed in"""
        r = self.client.get(reverse('Dashboard:MyDetails'))
        self.assertRedirects(r, reverse('GetInvolved'))

    def test_011_MyDetailsSignedIn(self):
        """Test that a logged in User gets to the Dashboard"""
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:MyDetails'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.MyDetails.__name__)
        self.assertTemplateUsed(r, "dashboard/pages/MyDetails.html")
        self.assertIsInstance(r.context[-1]['form'], forms.MyDetails)
        self.assertEqual(r.context[-1]['form']['email'].value(), self.user.email)

    def test_012_MyDetailsMainSubmit(self):
        """Test that the Details Page gets Posted Correctly - just change the email address for now"""
        ts = now()
        self.client.force_login(user=self.user)
        r = self.client.post(reverse('Dashboard:MyDetails'),
                             data={'email': 'tester@test.test.com',
                                   'submit': u'Save'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.MyDetails.__name__)
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
                             data={'submit': u'Change Password'})
        self.assertRedirects(r, reverse('Dashboard:PasswordReset'))

    def test_020_ChangePasswordNotLoggedin(self):
        r = self.client.get(reverse('Dashboard:PasswordReset'))
        self.assertRedirects(r, reverse('GetInvolved'))

    def test_021_ChangePasswordLoggedIn(self):
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:PasswordReset'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.PasswordReset.__name__)
        self.assertTemplateUsed(r, "dashboard/pages/PasswordChange.html")
        self.assertIsInstance(r.context[-1]['form'], RegisteredUsers.forms.PasswordReset)
        self.assertNotEqual(r.context[-1]['form']['uuid'].value(), '')

        # Check that the PasswordResetRequest instance has an expiry of today() + 1
        prr = RegisteredUsers.models.PasswordResetRequest.objects.get(uuid=r.context[-1]['form']['uuid'].value())
        self.assertEqual(prr.expiry - date.today(), timedelta(days=1))
        self.assertEqual(prr.user, self.user)

    def test_022_ChangePasswordSubmit(self):
        """Test that the change Password works correctly"""
        ts = now()

        prr = RegisteredUsers.models.PasswordResetRequest(user=self.user, expiry=date.today() + timedelta(days=1))
        prr.save()

        self.client.force_login(user=self.user)
        r = self.client.post(reverse('Dashboard:PasswordReset'),
                             data={'uuid': str(prr.uuid), 'newPassword': 'test', 'confirmPassword': 'test'})
        self.assertTemplateUsed(r, "dashboard/pages/PasswordChange.html")
        self.assertTrue('confirmation' in r.context[-1])

        # Check that the PasswordResetRequest instance is deleted
        with self.assertRaises(ObjectDoesNotExist):
            RegisteredUsers.models.PasswordResetRequest.objects.get(uuid=prr.uuid)
        self.assertEqual(authenticate(username='Tester', password='test'), self.user)

        # Check the Password change is recorded in the stats
        self.assertAlmostEqual(PageVisit.most_recent(document='Dashboard:PasswordReset', user=self.user).timestamp, ts,
                               delta=timedelta(milliseconds=500))

    def test_030_ChangePortraitSubmit(self):
        """ Test that a simple picture is uploaded """
        # create a blank 250x250 image
        with TDC() as tmp_dir:
            pic_file = os.path.join(tmp_dir,'my_pic.jpg')
            newImage = Image.new('RGB',(250,250), 'white')
            newImage.save(pic_file)
            self.client.force_login(user=self.user)
            r = self.client.post(reverse('Dashboard:MyDetails'),
                                        {'picture': open(pic_file, 'rb'),
                                         'submit': 'Save'} )
            self.assertEqual(r.status_code, 200)
            self.assertTrue('confirmation' in r.context[-1])
            self.cyclist.refresh_from_db()
            upload_path = self.cyclist.picture.name
            # Need to confirm - that the files are the same - and that the file is uploaded to the right place
            self.assertEqual(upload_path, os.path.join( 'portraits',self.user.username, 'portrait.jpg'))
            upload_pic = Image.open(os.path.join(settings.MEDIA_ROOT,upload_path))
            self.assertEqual(upload_pic.size, (250,250))

    def test_031_ChangePortraitError(self):
        """ Test that a simple picture is uploaded """
        # create a blank 250x250 image
        with TDC() as tmp_dir:
            pic_file = os.path.join(tmp_dir,'my_pic.jpg')
            newImage = Image.new('RGB',(200,200), 'white')
            newImage.save(pic_file)
            self.client.force_login(user=self.user)
            r = self.client.post(reverse('Dashboard:MyDetails'),
                                        {'picture': open(pic_file, 'rb'),
                                         'submit': 'Save'} )
            self.assertEqual(r.status_code, 200)
            self.assertIn(u'Picture is too small', r.context[-1]['form'].errors['picture'][0])

class CycleRoutes(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(first_name='Chester', last_name="Tester",
                                             username='Tester', email='tester@test.com',
                                             password='testtest')

        self.legs = [ cyclists.models.Leg(date=date(2020,07,10) + timedelta(days=10+c/2),
                                        name='Leg{}'.format(c), start='Town{}'.format(c+1), end='Town{}'.format(c+2),
                                        morning=c%2==0, distanceKM=17)
                 for c in range(0,6)]
        for l in self.legs:
            l.save()

        # Create and save 3 Legs - date offset of 10 days - so we can tweak the order if neccessary
        self.cyclist = cyclists.models.Cyclist.objects.get(user=self.user)

    def checkbox_status(self, content):
        soup = BeautifulSoup(content, 'html5lib')
        boxes = soup.select("input.checkbox")
        return dict([(box['value'], ('checked' in box.attrs)) for box in boxes if 'checked' in box.attrs])

    def test_010_CycleRoutesNotSignedIn(self):
        """Test that there is no access to the Dashboard when not signed in"""
        r = self.client.get(reverse('Dashboard:CycleRoutes'))
        self.assertRedirects(r, reverse('GetInvolved'))

    def test_011_CycleRoutesSignedIn(self):
        """Test that a logged in User gets to the Dashboard"""
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:CycleRoutes'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.CycleRoutes.__name__)
        self.assertTemplateUsed(r, "dashboard/pages/CycleRoutes.html")

    def test_012_RoutesNotSelected(self):
        """Test that with no routes currently selected - the routes appear in date order"""
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:CycleRoutes'))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "dashboard/pages/CycleRoutes.html")
        self.assertEqual(len(r.context[-1]['legs']), 6)
        self.assertSequenceEqual(r.context[-1]['legs'], self.legs)
        self.assertEqual(self.checkbox_status(r.content), {})

    def test_013_RoutesNotSelected(self):
        """Test that with no routes currently selected - the routes appear in date order - modfied date"""
        self.legs[2].date = self.legs[0].date - timedelta(days=2)
        self.legs[3].date = self.legs[0].date - timedelta(days=2)
        self.legs[2].save()
        self.legs[3].save()
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:CycleRoutes'))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "dashboard/pages/CycleRoutes.html")
        self.assertEqual(len(r.context[-1]['legs']), 6)
        self.assertSequenceEqual(r.context[-1]['legs'], self.legs[2:4] + self.legs[0:2] + self.legs[4:])
        self.assertEqual(self.checkbox_status(r.content), {})

    def test_020_RoutesSelected(self):
        """Test that with one routes currently selected - the routes appear in order - and the correct one selected"""
        self.cyclist.legs.add(self.legs[2])
        self.cyclist.legs.add(self.legs[3])
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:CycleRoutes'))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "dashboard/pages/CycleRoutes.html")
        self.assertEqual(len(r.context[-1]['legs']), 6)
        self.assertSequenceEqual(r.context[-1]['legs'],  self.legs)
        self.assertEqual(self.checkbox_status(r.content), {str(self.legs[2].pk): True,
                                                           str(self.legs[3].pk): True,})

    def test_021_RoutesSelected2(self):
        """Test that with one routes currently selected - the routes appear in order - and the correct one selected"""
        self.cyclist.legs.add(self.legs[2], self.legs[3])
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:CycleRoutes'))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "dashboard/pages/CycleRoutes.html")
        self.assertEqual(len(r.context[-1]['legs']), 6)
        self.assertSequenceEqual(r.context[-1]['legs'], self.legs)
        self.assertEqual(self.checkbox_status(r.content), {str(self.legs[2].pk): True,
                                                           str(self.legs[3].pk): True})

    def test_025_SelectRouteandPost(self):
        """Test that a selection of a checkbox is reflected into the database"""
        self.cyclist.legs.add(self.legs[2])
        self.client.force_login(user=self.user)
        r = self.client.post(reverse('Dashboard:CycleRoutes'),
                             data={'submit': 'Save',
                                   'selected': ('2', '3')})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.CycleRoutes.__name__)
        self.assertTemplateUsed(r, "dashboard/pages/CycleRoutes.html")
        self.assertTrue('confirmation' in r.context[-1])

        self.assertTrue(self.legs[0] not in self.cyclist.legs.all())
        self.assertTrue(self.legs[1] in self.cyclist.legs.all())
        self.assertTrue(self.legs[2] in self.cyclist.legs.all())
        self.assertTrue(self.legs[3] not in self.cyclist.legs.all())
        self.assertTrue(self.legs[4] not in self.cyclist.legs.all())
        self.assertTrue(self.legs[5] not in self.cyclist.legs.all())


class FundRaising(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(first_name='Chester', last_name="Tester",
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
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.Fundraising.__name__)
        self.assertTemplateUsed(r, "dashboard/base/dashboard_form.html")
        self.assertIsInstance(r.context[-1]['form'], forms.FundRaising)
        self.assertEqual(r.context[-1]['form'].instance, self.cyclist)

    def test_012_FundRaisingValuesShown(self):
        """Test that the form is populated correctly"""
        self.cyclist.targetAmount = 500
        self.cyclist.currentPledgedAmount = 40
        self.cyclist.save()
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:FundRaising'))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, "dashboard/pages/FundRaising.html")
        self.assertIsInstance(r.context[-1]['form'], forms.FundRaising)
        self.assertEqual(r.context[-1]['form'].instance, self.cyclist)
        self.assertEqual(r.context[-1]['form']['targetAmount'].value(), self.cyclist.targetAmount)
        self.assertEqual(r.context[-1]['form']['currentPledgedAmount'].value(), self.cyclist.currentPledgedAmount)
        self.assertContains(r, reverse('FundMe', kwargs={'username': self.user.username}))

    def test_015_FundRaisingValuesPost(self):
        """Test that the form is gets posted correctly"""
        self.cyclist.targetAmount = 500
        self.cyclist.currentPledgedAmount = 40
        self.cyclist.save()
        self.client.force_login(user=self.user)
        r = self.client.post(reverse('Dashboard:FundRaising'),
                             data={'targetAmount': 1000,
                                   'currentPledgedAmount': 80,
                                   'submit': 'Save'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.Fundraising.__name__)
        self.assertTemplateUsed(r, "dashboard/pages/FundRaising.html")
        self.assertTrue('confirmation' in r.context[-1])
        self.cyclist.refresh_from_db()
        self.assertEqual(self.cyclist.targetAmount, 1000)
        self.assertEqual(self.cyclist.currentPledgedAmount, 80)

    def test_020_FundRaisingStatementPost(self):
        """Test that the form is gets posted correctly"""
        statement = "this is a poor statement-like statement, that states things without stating anything."
        self.client.force_login(user=self.user)
        r = self.client.post(reverse('Dashboard:FundRaising'),
                             data={ 'targetAmount': self.cyclist.targetAmount,
                                     'currentPledgedAmount': self.cyclist.currentPledgedAmount,
                                     'statement': statement,
                                     'submit': 'Save'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.Fundraising.__name__)
        self.assertTemplateUsed(r, "dashboard/pages/FundRaising.html")
        self.assertTrue('confirmation' in r.context[-1])
        self.cyclist.refresh_from_db()
        self.assertEqual(self.cyclist.statement, statement)

class FundMe(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(first_name='Chester', last_name="Tester",
                                             username='Tester', email='tester@test.com',
                                             password='testtest')
        self.cyclist = cyclists.models.Cyclist.objects.get(user=self.user)

    def tearDown(self):
        pass

    def test_010_FundMeNotSignedIn(self):
        """Test that there is no access to the Dashboard when not signed in"""
        r = self.client.get(reverse('Dashboard:FundMe'))
        self.assertRedirects(r, reverse('GetInvolved'))

    def test_011_FundMeSignedIn(self):
        """Test that a logged in User gets to the Dashboard"""
        self.client.force_login(user=self.user)
        r = self.client.get(reverse('Dashboard:FundMe'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.resolver_match.func.__name__, views.FundMe.__name__)
        self.assertTemplateUsed(r, "SuffolkCycleRide/pages/fundme.html")
        self.assertEqual(r.context[-1]['cyclist'], self.cyclist)
        self.assertTrue('mockup' in r.context[-1])

        # Prove that the site menu is in the markup
        st = BeautifulSoup(r.content, 'html5lib')
        uls = st.select('ul.chevronbar')
        self.assertEqual(len(uls), 1, "Main menu bar not found")

        # Test the mockup values
