from django.test import TestCase

import models


class C001_TagCreationErrors(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_001_010_TagCreationErrorEmptyName(self):
        """Ensure that Tag Creation raises Exception when name is blank"""
        with self.assertRaises( ValueError ):
            t = models.Tag.create('')

    def test_001_011_TagCreationErrorNullName(self):
        """Ensure that Tag Creation raises Exception when name is None"""
        with self.assertRaises( ValueError ):
            t = models.Tag.create(None)

    def test_001_012_TagCreationErrorTooLong(self):
        """Ensure that Tag Creation raises Exception when name too long - 21 characters"""
        with self.assertRaises( ValueError ):
            t=models.Tag.create('a' * 21)


class C002_TagCreationNameTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_002_010_TagCreationNameNoSpaces(self):
        """Create a simple tag with a simple name"""
        t = models.Tag.create('parrot')
        self.assertEqual(t.name, 'parrot')

    def test_002_020_TagCreationNameWithSpaces(self):
        """Create a simple tag with a simple name"""
        t = models.Tag.create('Dead Parrot')
        self.assertEqual(t.name, 'Dead Parrot')

    def test_002_030_TagCreationTemporaryAsDefault(self):
        """Create a simple tag with a simple name"""
        t = models.Tag.create('Dead Parrot')
        self.assertEqual(t.name, 'Dead Parrot')
        self.assertEqual(t.is_permanent, False)

class C003_TagCreationSlugTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_003_010_TagCreationCheckSlugNoSpacesLowercase(self):
        """Create a tag with a name with no spaces and lowercase - check slug is created correctly"""
        t = models.Tag.create('parrot')
        self.assertEqual(t.slug, 'parrot')

    def test_003_015_TagCreationCheckSlugNoSpacesMixedcase(self):
        """Create a tag with a name with no spaces and lowercase - check slug is created correctly"""
        t = models.Tag.create('DeadParrot')
        self.assertEqual(t.slug, 'deadparrot')

    def test_003_020_TagCreationCheckSlugSpacesLowercase(self):
        """Create a tag with a name with no spaces and lowercase - check slug is created correctly"""
        t = models.Tag.create('dead parrot')
        self.assertEqual(t.slug, 'dead_parrot')

    def test_003_025_TagCreationCheckSlugSpacesMixedcase(self):
        """Create a tag with a name with no spaces and lowercase - check slug is created correctly"""
        t = models.Tag.create('Dead Parrot Sketch')
        self.assertEqual(t.slug, 'dead_parrot_sketch')


class C004_EntryCreationErrors(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_004_010_EntryCreationErrorEmptyName(self):
        """Create a Entry with an empty string title, should raise an exception"""
        with self.assertRaises(ValueError):
            e = models.Entry.create('')

    def test_004_015_EntryCreationErrorNullName(self):
        """Create a Entry with an None title, should raise an exception"""
        with self.assertRaises(ValueError):
            e = models.Entry.create(None)

    def test_004_017_EntryCreationErrorNameTooLong(self):
        """Create a Entry with a title, which is too long, should raise an exception"""
        with self.assertRaises(ValueError):
            e = models.Entry.create('a'*61)


class C005_EntryCreationTitleTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_005_010_EntryCreationTitle(self):
        """Create an Entry and confirm that nothing is rejected, and the title is validly stored"""
        e = models.Entry.create('This is a title')
        self.assertEqual(e.title, 'This is a title')

    def test_005_020_EntryCreationTestSlug(self):
        """Create an Entry and confirm that the slug is created correctly"""
        e = models.Entry.create('This is a title')
        self.assertEqual(e.slug, 'this_is_a_title')

class C006_EntryTagRelationship(TestCase):
    """Test extra functionality around the Entry <-> Tag relationship"""
    def setUp(self):
        self.python = models.Tag('Monty Python', is_permanent=True)
        self.python.save()
        self.fawltyTowers = models.Tag('Fawlty Towers', is_permanent=True)
        self.fawltyTowers.save()
        self.poletoPole = models.Tag('Pole to Pole', is_permanent=True)
        self.poletoPole.save()

        self.palin = models.Entry("Michael Palin")
        self.palin.save()
        self.cleese = models.Entry("John Cleese")
        self.cleese.save()

    def tearDown(self):
        pass

    def test_006_010_AddTagViaText(self):
        """Add a single existing tags - use one name, and not two"""
        self.palin.tag_text='Monty Python'
        self.assertItemsEqual( [self.python], self.palin.tags.all())

    def test_006_012_AddTagsViaText(self):
        """Add two Existing tags via tag_text property"""
        self.palin.tag_text='Monty Python, Pole to Pole'
        self.assertItemsEqual( [self.python, self.poletoPole], self.palin.tags.all())

    def test_006_014_ChangeTagViaText(self):
        """Change the tags - use one name, and not two"""
        self.palin.tag_text='Monty Python, Pole to Pole'
        self.assertItemsEqual( [self.python, self.poletoPole], self.palin.tags.all())
        self.palin.tag_text='Pole to Pole'
        self.assertItemsEqual( [self.poletoPole], self.palin.tags.all())

    def test_006_20_AddNewTagViaText(self):
        """Add a New tags via tag_text property"""
        tag_name = 'A Fish called Wanda'
        find = models.Tag.objects.filter(name=tag_name).count()
        self.assertEqual(find, 0)                                   # Check the tag does not exist

        self.cleese.tag_text=tag_name                               # Add the tag

        tag = models.Tag.objects.filter(name =tag_name)
        self.assertEqual( tag[0].name, tag_name)                   # Check that the tag has been created
        self.assertEqual( tag[0].is_permanent, False)

        self.assertItemsEqual( tag, self.cleese.tags.all())         # Check that the tag has been added.

    def test_006_020_TagReturnText(self):
        """Get tag names via tag_text return"""
        self.palin.tags = [self.python, self.poletoPole]
        txt = self.palin.tag_text
        self.assertTrue(self.python.name in txt)        # No Guaranteed ordering in tag_text
        self.assertTrue(self.poletoPole.name in txt)    # No Guaranteed ordering in tag_text

    def test_006_030_CheckRefCount(self):
        self.palin.tags = [self.python, self.poletoPole]
        self.cleese.tags = [self.python, self.fawltyTowers]

        self.assertEqual(self.python.ref_count(), 2)
        self.assertEqual(self.poletoPole.ref_count(), 1)
        self.assertEqual(self.fawltyTowers.ref_count(), 1)

    def test_006_040_TestTagDeletion(self):
        """Test that a tag is deleted when it is removed and the ref_count"""

        tag_name = 'A Fish called Wanda'
        self.assertEqual(models.Tag.objects.filter(name=tag_name).count(), 0)  # Check the tag does not exist

        self.cleese.tag_text=tag_name                                          # Add the tag
        tag = models.Tag.objects.get(name =tag_name)
        self.assertEqual(tag.ref_count(), 1)
        self.cleese.tag_text=''                                                # Remove the tag
        self.assertEqual(models.Tag.objects.filter(name=tag_name).count(), 0)  # Check the tag does not exist


    def test_006_042_TestTagDeletion(self):
        """Test that a tag is deleted when it is removed and the ref_count"""
        tag_name = 'A Fish called Wanda'
        tag = models.Tag.create(tag_name)
        self.assertEqual(tag.is_permanent, False)                               # Check the tag is temporary
        self.assertEqual(tag.ref_count(), 0)                                    # Check the tag does not exist

        self.cleese.tag_text=tag_name                                           # Add the tag to Mr Cleese

        self.assertEqual(tag.ref_count(), 1)

        self.cleese.tag_text=''                    # Remove the tag

        self.assertEqual(models.Tag.objects.filter(name=tag_name).count(), 0)  # Check the tag does not exist


    def test_006_045_TestTagDeletionMultipleAdditions(self):
        """Test that a tag is deleted when it is removed and the ref_count"""
        tag_name = 'A Fish called Wanda'

        self.cleese.tag_text= tag_name                               # Add the tag to Messers Cleese & Palin
        self.palin.tag_text = tag_name

        tag = models.Tag.objects.get(name =tag_name)
        self.assertEqual(tag.ref_count(), 2)                            # Check the tag exists
        self.cleese.tag_text=''                                         # Remove the tag from Cleese
        self.assertEqual(tag.ref_count(), 1)                            # Check the tag exists
        self.palin.tag_text= ''

        self.assertEqual(models.Tag.objects.filter(name=tag_name).count(), 0)  # Check the tag does not exist

    def test_006_050_TestTagRetention(self):
        """Test that a permanent tag is retained when it is removed and the ref_count is zero"""

        self.assertEqual(self.python.is_permanent, True)     # Check the tag exists and is permanent
        self.cleese.tag_text=self.python.name                # Add the tag
        self.assertEqual(self.python.ref_count(), 1)         # Check the  ref count is incremented
        self.cleese.tag_text=''                              # Remove the tag
        self.assertEqual(self.python.ref_count(), 0)         # Check the tag still exists with a ref_count of zero


class C007_TestViews(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass