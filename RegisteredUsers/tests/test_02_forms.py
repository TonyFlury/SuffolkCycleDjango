# coding=utf-8
"""
# SuffolkCycle : Implementation of test_02_forms.py

Summary :
    <summary of module/class being implemented>
Use Case :
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from RegisteredUsers import forms, models
from datetime import date, timedelta


class NewUserForm(TestCase):
    """Test the new user Form

        Conditions to test
            First name & Last name are mandatory (same error message for both).
            email is mandatory and unique
            username is mandatory and unique
            password is mandatory

        Operations :
            1) form.is_valid() must identify and report all the above errors.
            2) form.save() must save the user correctly

        Excluded :
            1) Form provides a login method - will be tested via views not here
            2) Not all fields are tested during form.save() test
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_010_NewUserNoName(self):
        """Test error generated when neither first or last name is provided"""
        f = forms.NewUserForm(data={'email': 'tester@test.com',
                                    'username': 'testertestington',
                                    'password': 'testertester',
                                    'confirm_password': 'testertester'})
        self.assertFalse(f.is_valid())
        self.assertEqual(f.errors, {'first_name': [u'You must provide both your first and last name']})

    def test_011_NewUserNoFirstName(self):
        """Test error generated when first name is not provided"""
        f = forms.NewUserForm(data={'last_name': 'Tester',
                                    'email': 'tester@test.com',
                                    'username': 'testertestington',
                                    'password': 'testertester',
                                    'confirm_password': 'testertester'})
        self.assertFalse(f.is_valid())
        self.assertEqual(f.errors, {'first_name': [u'You must provide both your first and last name']})

    def test_012_NewUserNoLastName(self):
        """Test error generated when last name is not provided"""
        f = forms.NewUserForm(data={'first_name': 'Chester',
                                    'email': 'tester@test.com',
                                    'username': 'testertestington',
                                    'password': 'testertester',
                                    'confirm_password': 'testertester'})
        self.assertFalse(f.is_valid())
        self.assertEqual(f.errors, {'last_name': [u'You must provide both your first and last name']})

    def test_013_NewUserNoEmail(self):
        """Test error generated when email address is not provided"""
        f = forms.NewUserForm(data={'first_name': 'Chester',
                                    'last_name': 'Tester',
                                    'username': 'testertestington',
                                    'password': 'testertester',
                                    'confirm_password': 'testertester'})
        self.assertFalse(f.is_valid())
        self.assertEqual(f.errors, {'email': [u'You must provide an email address']})

    def test_014_NewUserNoUserName(self):
        """Test error generated when username is not provided"""
        f = forms.NewUserForm(data={'first_name': 'Chester',
                                    'last_name': 'Tester',
                                    'email': 'tester@test.com',
                                    'password': 'testertester',
                                    'confirm_password': 'testertester'})
        self.assertFalse(f.is_valid())
        self.assertEqual(f.errors, {'username': [u'You must provide a username']})

    def test_015_NewUserNoPassword(self):
        """Test error generated when password is not provided"""
        f = forms.NewUserForm(data={'first_name': 'Chester',
                                    'last_name': 'Tester',
                                    'email': 'tester@test.com',
                                    'username': 'testertestington',
                                    'confirm_password': 'testertester'})
        self.assertFalse(f.is_valid())
        self.assertEqual(f.errors, {'password': [u'You must provide a password']})

    def test_016_NewUserNoConfirmationPassword(self):
        """Test error generated when confirmation password is not provided"""
        f = forms.NewUserForm(data={'first_name': 'Chester',
                                    'last_name': 'Tester',
                                    'email': 'tester@test.com',
                                    'username': 'testertestington',
                                    'password': 'testertester'})
        self.assertFalse(f.is_valid())
        self.assertEqual(f.errors, {'confirm_password': [u'You must re-enter the password']})

    def test_017_NewUserPasswordNotConfirmed(self):
        """Test error generated when password and confirmation password are different"""
        f = forms.NewUserForm(data={'first_name': 'chester',
                                    'last_name': 'tester',
                                    'email': 'tester@test.com',
                                    'username': 'testertestington',
                                    'password': 'testertester',
                                    'confirm_password': 'testertester1'})
        self.assertFalse(f.is_valid())
        self.assertEqual(f.errors, {'confirm_password': [u'Passwords do not match']})

    def test_020_NewUserOK(self):
        """Test that a valid user entry validates correctly"""
        f = forms.NewUserForm(data={'first_name': 'Chester',
                                    'last_name': 'Tester',
                                    'email': 'tester@test.com',
                                    'username': 'testertestington',
                                    'password': 'testertester',
                                    'confirm_password': 'testertester'})
        self.assertTrue(f.is_valid())
        self.assertEqual(f.errors, {})

    def test_021_NewUserSave(self):
        """Test that a valid user entry is saved correctly"""
        f = forms.NewUserForm(data={'first_name': 'Chester',
                                    'last_name': 'Tester',
                                    'email': 'tester@test.com',
                                    'username': 'testertestington',
                                    'password': 'testertester',
                                    'confirm_password': 'testertester'})
        self.assertTrue(f.is_valid())
        self.assertEqual(f.errors, {})
        f.save()
        u = models.User.objects.all()
        self.assertEqual(len(u), 1)
        self.assertEqual(u[0].first_name, "Chester")
        self.assertEqual(u[0].last_name, "Tester")

    def test_031_NewUserNoDuplicateEMails(self):
        """Test that a duplicate emails are trapped and the 2nd user cannot be created"""
        f = forms.NewUserForm(data={'first_name': 'Chester',
                                    'last_name': 'Tester',
                                    'email': 'tester@test.com',
                                    'username': 'testertestington',
                                    'password': 'testertester',
                                    'confirm_password': 'testertester'})
        self.assertTrue(f.is_valid())
        f.save()
        f1 = forms.NewUserForm(data={'first_name': 'Chester',
                                     'last_name': 'Tester',
                                     'email': 'tester@test.com',
                                     'username': 'testertestington1',
                                     'password': 'testertester1',
                                     'confirm_password': 'testertester1'})
        self.assertFalse(f1.is_valid())

    def test_032_NewUserNoDuplicateUsername(self):
        """Test that a duplicate usernames are trapped and the 2nd user cannot be created"""
        f = forms.NewUserForm(data={'first_name': 'Chester',
                                    'last_name': 'Tester',
                                    'email': 'tester@test.com',
                                    'username': 'testertestington',
                                    'password': 'testertester',
                                    'confirm_password': 'testertester'})
        self.assertTrue(f.is_valid())
        f.save()
        f1 = forms.NewUserForm(data={'first_name': 'Chester',
                                     'last_name': 'Tester',
                                     'email': 'tester1@test.com',
                                     'username': 'testertestington',
                                     'password': 'testertester',
                                     'confirm_password': 'testertester'})
        self.assertFalse(f1.is_valid())


class SignInForm(TestCase):
    """ Test SignIn Form

        Conditions to test :
            1) Username/password must represent a valid user.

        Operations :
            1) clean - validates that the entered credentials are for a valid user.
            2) save - authenticates and logs on - can't log a user in without a session -
                      testing deferred to View testing.
    """

    def setUp(self):
        self.chester = User.objects.create_user(first_name='Chester',
                                                last_name='Tester',
                                                email='tester@test.com',
                                                username='testertestington',
                                                password='testertester')

    def tearDown(self):
        pass

    def test_010_SignInNoUsername(self):
        f = forms.SignInForm(data={'password': 'testertester'})
        self.assertFalse(f.is_valid())
        self.assertEqual(f.errors, {'username': [u'Username is required']})

    def test_011_SignInNoPassword(self):
        f = forms.SignInForm(data={'username': 'testertestington'})
        self.assertFalse(f.is_valid())
        self.assertEqual(f.errors, {'password': [u'Password is required']})

    def test_012_SignInPasswordNotRecognised(self):
        f = forms.SignInForm(data={'username': 'testertester', 'password': 'testertester'})
        self.assertFalse(f.is_valid())
        self.assertEqual(f.errors, {'__all__':
                                    [u'Unrecognised Username/Password combination - please correct and try again']})

    def test_014_SignInOk(self):
        f = forms.SignInForm(data={'username': 'testertestington', 'password': 'testertester'})
        self.assertTrue(f.is_valid())  # This will aunthenticate the user/password
        # Can't login without a valid session - i.e. need to do it via a view


class PasswordResetRequestForm(TestCase):
    """ Test Password Reset Request Form

        Conditions to test :
            1) Email address must exist as a user.
            2) Completion of form creates a Password ResetRequest

        Operations :
            is_valid : Ensures that email address represents an existing user
            save : Creates the Password ResetRequest instance.
    """

    def setUp(self):
        self.chester = User.objects.create_user(first_name='Chester',
                                                last_name='Tester',
                                                email='tester@test.com',
                                                username='testertestington',
                                                password='testertester')

    def tearDown(self):
        pass

    def test_010_PasswordResetRequestNoEmail(self):
        f = forms.PasswordResetRequest(data={})
        self.assertFalse(f.is_valid())
        self.assertEqual(f.errors, {'email': [u'Enter your email address']})

    def test_011_PasswordResetRequestInvalidEmail(self):
        f = forms.PasswordResetRequest(data={'email': 'blahblah'})
        self.assertFalse(f.is_valid())
        self.assertEqual(f.errors, {'email': [u"Email '{}' is not registered on this system".format('blahblah')]})

    def test_012_PasswordResetRequestOK(self):
        f = forms.PasswordResetRequest(data={'email': 'tester@test.com'})
        self.assertTrue(f.is_valid())
        prr = f.save()
        q = models.PasswordResetRequest.objects.all()
        self.assertEqual(len(q), 1)
        self.assertEqual(q[0], prr)
        self.assertEqual(q[0].expiry, date.today() + timedelta(days=14))


class PasswordReset(TestCase):
    """ Test Password reset request

        conditions :
            Password reset request instance with relevant uuid must exist - ensured by calling view
            password reset request cannot have expired - ensured by calling view
            passwords are mandatory and must match
            password is changed correctly - tested by authentication
    """
    #Todo - Need to test for specific error messages

    def setUp(self):
        self.chester = User.objects.create_user(first_name='Chester',
                                                last_name='Tester',
                                                email='tester@test.com',
                                                username='testertestington',
                                                password='testertester')
        self.valid_prr = models.PasswordResetRequest(user=self.chester, expiry=date.today() + timedelta(days=14))
        self.valid_prr.save()

    def tearDown(self):
        pass

    def test_010_PasswordResetNoPassword(self):
        """Test Password Reset when no password is passed"""
        f = forms.PasswordReset(data={'uuid': self.valid_prr.uuid})
        self.assertFalse(f.is_valid())

    def test_011_PasswordResetNoConfirmPassword(self):
        """Test Password Reset when no confirmed password is passed"""
        f = forms.PasswordReset(data={'uuid': self.valid_prr.uuid, 'newPassword': 'test1'})
        self.assertFalse(f.is_valid())

    def test_012_PasswordResetNoNewPassword(self):
        """Test Password Reset when no new password is passed"""
        f = forms.PasswordReset(data={'uuid': self.valid_prr.uuid, 'confirmPassword': 'test1'})
        self.assertFalse(f.is_valid())

    def test_013_PasswordResetPasswordNoMatch(self):
        """Test Password Reset when passwords don't match"""
        f = forms.PasswordReset(data={'uuid': self.valid_prr.uuid, 'newPassword': 'test1', 'confirmPassword': 'test2'})
        self.assertFalse(f.is_valid())

    def test_014_PasswordResetPasswordOk(self):
        """Test Password Reset when passwords don't match"""
        f = forms.PasswordReset(data={'uuid': self.valid_prr.uuid, 'newPassword': 'test', 'confirmPassword': 'test'})
        self.assertTrue(f.is_valid())
        f.save()
        u = authenticate(username=self.chester.username, password='test')
        self.assertEqual(u, self.chester)
