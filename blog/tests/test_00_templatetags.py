#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of test_00_templatetags.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""
from django.test import TestCase
from django.template import Template, Context
from django.core.urlresolvers import reverse

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '22 Feb 2016'

class C000_TestTemplateTags(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @staticmethod
    def render(string, length=None, center=None):
        template = Template("{% load blog_tags %}"+\
                            "{% ellipsis string "+\
                            ('length={} '.format(length) if length else '') +\
                            ('center={} '.format(center) if center else '') +\
                            "%}")
        return template.render(Context({'string':string, 'length':length, 'center':center}))

    def test_000_001_AddEllipsisEndShort(self):
        text = self.render( 'string_value', 30, False)
        self.assertEqual('string_value',text)

    def test_000_002_AddEllipsisCenterShort(self):
        text = self.render( 'string_value', 30, True)
        self.assertEqual('string_value',text)

    def test_000_003_AddEllipsisEnd(self):
        text = self.render( 'string_value', 9, False)
        self.assertEqual('string...',text)

    def test_000_004_AddEllipsisCenterEven(self):
        """Test Center ellipsis on a string where the string """
        text = self.render( 'string_value', 9, True)
        self.assertEqual('str...lue',text)

    def test_000_005_AddEllipsisCenterOdd(self):
        """Test Center ellipsis on a string where length-3 is not divisible by 2"""
        text = self.render( 'string_value1', 9, True)
        self.assertEqual('str...ue1',text)

    def test_010_010_YearVisible(self):
        """Test Year visible template tag"""
        template = Template('{% load blog_tags %}{% year_visible %}')
        text = template.render( Context({ 'year':{'grouper':2015},
                                          'archive':{'display_year':2015}} ) )
        self.assertEqual('archive-visible', text)

    def test_010_011_YearNotVisible(self):
        """Test Year visible template tag"""
        template = Template('{% load blog_tags %}{% year_visible %}')
        text = template.render( Context({ 'year':{'grouper':2015},
                                          'archive':{'display_year':2016}} ) )
        self.assertEqual('', text)

    def test_010_015_MonthVisible(self):
        """Test Month visible template tag"""
        template = Template('{% load blog_tags %}{% month_visible %}')
        text = template.render( Context({ 'year':{'grouper':2015},
                                          'month':{'grouper':11},
                                          'archive':{'display_year':2015, 'display_month':11}} ) )
        self.assertEqual('archive-visible', text)

    def test_010_016_MonthNotVisibleMonthDifferent(self):
        """Test Month visible template tag"""
        template = Template('{% load blog_tags %}{% month_visible %}')
        text = template.render( Context({ 'year':{'grouper':2015},
                                          'month':{'grouper':11},
                                          'archive':{'display_year':2015, 'display_month':10}} ) )
        self.assertEqual('', text)

    def test_010_017_MonthNotVisib1eYearDifferent(self):
        """Test Month visible template tag"""
        template = Template('{% load blog_tags %}{% month_visible %}')
        text = template.render( Context({ 'year':{'grouper':2015},
                                          'month':{'grouper':11},
                                          'archive':{'display_year':2016, 'display_month':11}} ) )
        self.assertEqual('', text)

    def test_010_020_YearUrl(self):
        """Test that Year URL is generated correctly"""
        template = Template('{% load blog_tags %}{% year_url %}')
        text = template.render( Context({ 'year':{'grouper':2015} } ))
        self.assertEqual(reverse('Blog:Archive', kwargs={'year':2015}), text)

    def test_010_021_MonthUrl(self):
        """Test that Month URL is generated correctly"""
        template = Template('{% load blog_tags %}{% month_url %}')
        text = template.render( Context({ 'year':{'grouper':2015},
                                          'month':{'grouper':11} } ))
        self.assertEqual(reverse('Blog:Archive', kwargs={'year':2015,'month':11}), text)

    def test_010_030_PrevPagerUrlYear(self):
        """Test Prev Page for Year argument when prev_page doesn't exist"""
        template = Template('{% load blog_tags %}{% prev_page_url %}')
        text = template.render( Context({ 'args':{'year':2015} } ))
        self.assertEqual('', text)

    def test_010_031_PrevPagerUrlYear(self):
        """Test Prev Page for Year argument when prev_page exist"""
        template = Template('{% load blog_tags %}{% prev_page_url %}')
        text = template.render( Context({'args':{'year':2015,'prev_page':2} } ))
        self.assertHTMLEqual(
                '<a href="{}">Previous</a>'.format(reverse('Blog:Archive', kwargs={'year':2015,'page':2})),
                text)

    def test_010_035_NextPagerUrlYear(self):
        """Test Next Page for Year argument when next_page doesn't exist"""
        template = Template('{% load blog_tags %}{% prev_page_url %}')
        text = template.render( Context({ 'args':{'year':2015} } ))
        self.assertEqual('', text)

    def test_010_036_NextPagerUrlYear(self):
        """Test Next Page for Year argument when next_page exists"""
        template = Template('{% load blog_tags %}{% next_page_url %}')
        text = template.render( Context({'args':{'year':2015,'next_page':2} } ))
        self.assertHTMLEqual(
                '<a href="{}">Next</a>'.format(reverse('Blog:Archive', kwargs={'year':2015,'page':2})),
                text)

    def test_010_040_PrevPagerUrlYearMonth(self):
        """Test Prev Page for Year/Month argument when prev_page doesn't exist"""
        template = Template('{% load blog_tags %}{% prev_page_url %}')
        text = template.render( Context({ 'args':{'year':2015, 'month':11} } ))
        self.assertEqual('', text)

    def test_010_041_PrevPagerUrlYearMonth(self):
        """Test Prev Page for Year/Month argument when prev_page exist"""
        template = Template('{% load blog_tags %}{% prev_page_url %}')
        text = template.render( Context({'args':{'year':2015,'month':11,'prev_page':2} } ))
        self.assertHTMLEqual(
                '<a href="{}">Previous</a>'.format(reverse('Blog:Archive', kwargs={'year':2015, 'month':11,'page':2})),
                text)

    def test_010_045_NextPagerUrlYearMonth(self):
        """Test Next Page for Year/Month argument when next_page doesn't exist"""
        template = Template('{% load blog_tags %}{% prev_page_url %}')
        text = template.render( Context({ 'args':{'year':2015, 'month':11} } ))
        self.assertEqual('', text)

    def test_010_046_NextPagerUrlYearMonth(self):
        """Test Next Page for Year/Month argument when next_page exist"""
        template = Template('{% load blog_tags %}{% next_page_url %}')
        text = template.render( Context({'args':{'year':2015,'month':11,'next_page':2} } ))
        self.assertHTMLEqual(
                '<a href="{}">Next</a>'.format(reverse('Blog:Archive', kwargs={'year':2015,'month':11,'page':2})),
                text)

    def test_010_050_PrevPagerUrlSearch(self):
        """Test Prev Page for Tag Search when prev_page doesn't exist"""
        template = Template('{% load blog_tags %}{% prev_page_url %}')
        text = template.render( Context({ 'args':{'tag_slug':'Hello'} } ))
        self.assertEqual('', text)

    def test_010_051_PrevPagerUrlSearch(self):
        """Test Prev Page for Tag Search when prev_page exist"""
        template = Template('{% load blog_tags %}{% prev_page_url %}')
        text = template.render( Context({ 'args':{'tag_slug':'Hello', 'prev_page':1} } ))
        self.assertHTMLEqual(
                '<a href="{}">Previous</a>'.format(reverse('Blog:Search', kwargs={'tag_slug':'Hello','page':1})),
                text)

    def test_010_055_NextvPagerUrlSearch(self):
        """Test Next Page for Tag Search when next_page doesn't exist"""
        template = Template('{% load blog_tags %}{% next_page_url %}')
        text = template.render( Context({ 'args':{'tag_slug':'Hello'} } ))
        self.assertEqual('', text)

    def test_010_053_NextPagerUrlSearch(self):
        """Test Next Page for Tag Search when next_page exist"""
        template = Template('{% load blog_tags %}{% next_page_url %}')
        text = template.render( Context({ 'args':{'tag_slug':'Hello', 'next_page':2 } } ))
        self.assertHTMLEqual(
                '<a href="{}">Next</a>'.format(reverse('Blog:Search', kwargs={'tag_slug':'Hello','page':2})),
                text)