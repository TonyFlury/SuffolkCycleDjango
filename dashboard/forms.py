#!/usr/bin/env python
# coding=utf-8
"""
# SuffolkCycleDjango : Implementation of forms.py

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
__created__ = '23 Jan 2016'

from django.core.files.uploadedfile import TemporaryUploadedFile
from django.conf import settings
from django.contrib.auth.models import User
from django import forms
import cyclists.models

from SuffolkCycleRide.EnhancedForms import CombinedFormBase

from cyclists.models import Cyclist

from StringIO import StringIO
from PIL import Image


class PictureUpload(forms.ModelForm):
    """ Simple form to allow uploading of portrait picture to picture field on Cyclist Model"""
    class Meta:
        model = Cyclist
        fields = ['picture']
        labels = {'picture' : u"Portrait",}

    def clean_picture(self):
        """ Ensure that picture is big enough (width & height >= PORTRAIT_PICTURE_MIN_DIMENSION
                1) Clears the picture field in the field isn't an uploaded file
                2) Detects the size of the uploaded image, and create ValidationError if neccessary
                3) Resize the image so it conforms with the minimum size - minimize the space used
        """
        min_size = settings.PORTRAIT_PICTURE_MIN_DIMENSION

        # If user has ticked to delete his portrait - then the picture attribute can be False
        if not self.cleaned_data['picture']:
            self.cleaned_data['picture'] = ''
            return ''

        # Grab content of the Uploaded file and validate size - use StringIO to keep
        image_file = self.cleaned_data['picture']
        image_data = StringIO(image_file.read())
        image = Image.open(image_data)
        w, h = image.size
        if min(w,h) < min_size:
            raise forms.ValidationError('Picture is too small : must be a minimum of %(min)s x %(min)s pixels',
                                        code='invalid',
                                        params={'min':min_size} )

        # Resize image to ensure that the smallest size conforms to PORTRAIT_PICTURE_MIN_DIMENSION
        ratio = max(min_size/float(w), min_size/float(h))
        pic = image.resize((int(w*ratio), int(h*ratio)), Image.ANTIALIAS)

        new_image = StringIO()
        pic.save(new_image, 'JPEG', quality=90)

        # Create a new File for the resized image - can't simply overwrite contents of old file.
        new_Temp = TemporaryUploadedFile( name=image_file.name,
                                          content_type= image_file.content_type,
                                          content_type_extra=image_file.content_type_extra,
                                          charset=image_file.charset,
                                          size = new_image.len)
        new_Temp.write(new_image.getvalue())
        
        self.cleaned_data['picture'] = new_Temp
        return self.cleaned_data['picture']

class UserDetails(forms.ModelForm):
    # noinspection PyClassicStyleClass
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = { 'first_name': forms.fields.TextInput(attrs={'size':15,'label':"First Name"}),
                    'last_name': forms.fields.TextInput(attrs={'size':15,'label':"Last Name"}),
                    'email': forms.fields.EmailInput(attrs={'size':30,'label':'Email'}), }

class MyDetails(CombinedFormBase):
    form_classes = [UserDetails, PictureUpload]

class FundRaising(forms.ModelForm):
    class Meta:
        model = cyclists.models.Cyclist
        fields = ['targetAmount', 'currentPledgedAmount', 'fundraising_site']
        widgets = {'targetAmount' : forms.fields.TextInput(attrs={'size':7,'pattern':'(\d*.\d{2})|(\d+)','min':'0'}),
                   'currentPledgedAmount' : forms.fields.TextInput(attrs={'size':7,'pattern':'(\d*.\d{2})|(\d+)','min':'0'}),
                   'fundraising_site' : forms.URLInput(attrs={'size':40})}
        help_texts = {'targetAmount':'How much do you hope to raise',
                      'currentPledgedAmount': 'How much do you currently have pledged',
                      'fundraising_site' : 'Your fundraising site on MyDonate.com, FundMe.com or similar' }
        labels = {'targetAmount' : u"Target £",
                  'currentPledgedAmount' : u'Current Pledges £',
                  'fundraising_site' : 'Fundraising Site'}