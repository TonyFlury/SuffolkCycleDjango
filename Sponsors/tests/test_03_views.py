from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from datetime import datetime
from Sponsors import views
from Sponsors import models
from Sponsors import forms


class C010_test_OpportunityPage(TestCase):

    def setUp(self):
        self.opp1 = models.Opportunity(name='opp1', value=1)
        self.opp1.save()
        self.opp2 = models.Opportunity(name='opp2', value=2)
        self.opp2.save()
        self.opp3 = models.Opportunity(name='opp3', max_value=3)
        self.opp3.save()
        self.opp4 = models.Opportunity(name='opp4', value=4)
        self.opp4.save()
        self.client = Client()

    def test_010_001_basic_get(self):
        p = self.client.get(reverse('Sponsorship:Main'))
        self.assertEqual(p.status_code,200)
        self.assertEqual(p.resolver_match.func.__name__, views.main.__name__)

    def test_010_002_basic_get_template_check(self):
        p = self.client.get(reverse('Sponsorship:Main'))
        self.assertEqual(p.templates[0].name, 'Sponsors/main.html')

    def test_010_003_basic_get_context_check(self):
        p = self.client.get(reverse('Sponsorship:Main'))
        self.assertEqual(len(p.context[-1]['available']), 4)
        self.assertSequenceEqual(p.context[-1]['available'], [self.opp1, self.opp2, self.opp3, self.opp4])

    def test_010_010_test_unavailable(self):
        self.opp2.available = False
        self.opp2.save()
        p = self.client.get(reverse('Sponsorship:Main'))
        self.assertEqual(len(p.context[-1]['available']), 3)
        self.assertSequenceEqual(p.context[-1]['available'], [self.opp1, self.opp3, self.opp4])

    def test_010_020_test_taken(self):
        self.opp3.taken = True
        self.opp3.save()
        p = self.client.get(reverse('Sponsorship:Main'))
        self.assertEqual(len(p.context[-1]['available']), 3)
        self.assertSequenceEqual(p.context[-1]['available'], [self.opp1, self.opp2, self.opp4])

    def test_010_030_test_value_changed(self):
        self.opp3.value=10
        self.opp3.save()
        p = self.client.get(reverse('Sponsorship:Main'))
        self.assertEqual(len(p.context[-1]['available']), 4)
        self.assertSequenceEqual(p.context[-1]['available'], [self.opp1, self.opp2, self.opp4, self.opp3])


class C020_test_InterestPage(TestCase):
    def setUp(self):
        self.opp1 = models.Opportunity(name='opp1', value=1)
        self.opp1.save()
        self.client = Client()

    def tearDown(self):
        pass

    def test_020_001_InterestPageGet(self):
        p = self.client.get(reverse('Sponsorship:interest', kwargs={'opportunity_slug':self.opp1.slug}))
        self.assertEqual(p.status_code,200)
        self.assertEqual(p.resolver_match.func.__name__, views.interest.as_view().__name__)

    def test_020_002_InterestPageGet_template(self):
        p = self.client.get(reverse('Sponsorship:interest', kwargs={'opportunity_slug':self.opp1.slug}))
        self.assertEqual(p.templates[0].name, 'Sponsors/communicate.html')

    def test_020_003_InterestPageGet_context(self):
        p = self.client.get(reverse('Sponsorship:interest', kwargs={'opportunity_slug':self.opp1.slug}))
        self.assertIsInstance(p.context[-1]['form'], forms.Communications )
        self.assertEqual(p.context[-1]['form']['opportunity'].value(), self.opp1.id)
        self.assertEqual(p.context[-1]['description'],
                         'Thank you for your interest in sponsoring our {}.\n'
                         'Please complete the form, and we will contact you shortly.'.format(self.opp1.name) )

    def test_020_010_InterestPagePost(self):
        p = self.client.post(reverse('Sponsorship:interest', kwargs={'opportunity_slug':self.opp1.slug}),
                             data={'opportunity':self.opp1.id,
                              'name':'test Sponsor',
                              'communication_preference':'telephone',
                              'telephone':'11111111111'})
        self.assertEqual(p.templates[0].name, 'Sponsors/communicate.html')
        self.assertEqual(p.context[-1]['confirmation'],True)
        sp = models.Sponsor.objects.all()
        self.assertEqual(len(sp),1)
        self.assertEqual(sp[0].name, 'test Sponsor')
        self.assertEqual(sp[0].potential, True)
        self.assertTrue(self.opp1 in sp[0].potentials.all())