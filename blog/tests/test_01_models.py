import django.test

import blog.models


class C010_TagCreationNameTests(django.test.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_010_010_TagCreationNameNoSpaces(self):
        """Create a simple tag with a simple name"""
        t = blog.models.Tag(name='parrot')
        t.save()
        self.assertEqual(t.name, 'parrot')

    def test_010_020_TagCreationNameWithSpaces(self):
        """Create a simple tag with a simple name"""
        t = blog.models.Tag(name='Dead Parrot')
        t.save()
        self.assertEqual(t.name, 'Dead Parrot')

    def test_010_030_TagCreationTemporaryAsDefault(self):
        """Create a simple tag with a simple name"""
        t = blog.models.Tag(name='Dead Parrot')
        t.save()
        self.assertEqual(t.name, 'Dead Parrot')
        self.assertEqual(t.is_permanent, False)


class C015_TagCreationSlugTests(django.test.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_015_010_TagCreationCheckSlugNoSpacesLowercase(self):
        """Create a tag with a name with no spaces and lowercase - check slug is created correctly"""
        t = blog.models.Tag(name='parrot')
        t.save()
        self.assertEqual(t.slug, 'parrot')

    def test_015_015_TagCreationCheckSlugNoSpacesMixedcase(self):
        """Create a tag with a name with no spaces and lowercase - check slug is created correctly"""
        t = blog.models.Tag(name='DeadParrot')
        t.save()
        self.assertEqual(t.slug, 'deadparrot')

    def test_015_020_TagCreationCheckSlugSpacesLowercase(self):
        """Create a tag with a name with no spaces and lowercase - check slug is created correctly"""
        t = blog.models.Tag(name='dead parrot')
        t.save()
        self.assertEqual(t.slug, 'dead-parrot')

    def test_015_025_TagCreationCheckSlugSpacesMixedcase(self):
        """Create a tag with a name with no spaces and lowercase - check slug is created correctly"""
        t = blog.models.Tag(name='Dead Parrot Sketch')
        t.save()
        self.assertEqual(t.slug, 'dead-parrot-sketch')


class C020_EntryCreationTitleTests(django.test.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_020_010_EntryCreationTitle(self):
        """Create an Entry and confirm that nothing is rejected, and the title is validly stored"""
        e = blog.models.Entry(title='This is a title')
        e.save()
        self.assertEqual(e.title, 'This is a title')

    def test_020_020_EntryCreationTestSlug(self):
        """Create an Entry and confirm that the slug is created correctly"""
        e = blog.models.Entry(title='This is a title')
        e.save()
        self.assertEqual(e.slug, 'this-is-a-title')

class C025_EntryTagRelationship(django.test.TestCase):
    """Test extra functionality around the Entry <-> Tag relationship"""
    def setUp(self):
        self.python = blog.models.Tag(name='Monty Python', is_permanent=True)
        self.python.save()
        self.fawltyTowers = blog.models.Tag(name='Fawlty Towers', is_permanent=True)
        self.fawltyTowers.save()
        self.poletoPole = blog.models.Tag(name='Pole to Pole', is_permanent=True)
        self.poletoPole.save()

        self.palin = blog.models.Entry(title="Michael Palin")
        self.palin.save()
        self.cleese = blog.models.Entry(title="John Cleese")
        self.cleese.save()

    def tearDown(self):
        pass

    def test_025_010_AddTagViaText(self):
        """Add a single existing tags - use one name, and not two"""
        self.palin.tag_text='Monty Python'
        self.assertItemsEqual( [self.python], self.palin.tags.all())

    def test_025_012_AddTagsViaText(self):
        """Add two Existing tags via tag_text property"""
        self.palin.tag_text='Monty Python, Pole to Pole'
        self.assertItemsEqual( [self.python, self.poletoPole], self.palin.tags.all())

    def test_025_014_ChangeTagViaText(self):
        """Change the tags - use one name, and not two"""
        self.palin.tag_text='Monty Python, Pole to Pole'
        self.assertItemsEqual( [self.python, self.poletoPole], self.palin.tags.all())
        self.palin.tag_text='Pole to Pole'
        self.assertItemsEqual( [self.poletoPole], self.palin.tags.all())

    def test_025_20_AddNewTagViaText(self):
        """Add a New tags via tag_text property"""
        tag_name = 'A Fish called Wanda'
        find = blog.models.Tag.objects.filter(name=tag_name).count()
        self.assertEqual(find, 0)                                   # Check the tag does not exist

        self.cleese.tag_text=tag_name                               # Add the tag

        tag = blog.models.Tag.objects.filter(name =tag_name)
        self.assertEqual( tag[0].name, tag_name)                   # Check that the tag has been created
        self.assertEqual( tag[0].is_permanent, False)

        self.assertItemsEqual( tag, self.cleese.tags.all())         # Check that the tag has been added.

    def test_025_020_TagReturnText(self):
        """Get tag names via tag_text return"""
        self.palin.tags = [self.python, self.poletoPole]
        txt = self.palin.tag_text
        self.assertTrue(self.python.name in txt)        # No Guaranteed ordering in tag_text
        self.assertTrue(self.poletoPole.name in txt)    # No Guaranteed ordering in tag_text

    def test_025_030_CheckRefCount(self):
        self.palin.tags = [self.python, self.poletoPole]
        self.cleese.tags = [self.python, self.fawltyTowers]

        self.assertEqual(self.python.ref_count(), 2)
        self.assertEqual(self.poletoPole.ref_count(), 1)
        self.assertEqual(self.fawltyTowers.ref_count(), 1)

    def test_025_040_TestTagDeletion(self):
        """Test that a tag is deleted when it is removed and the ref_count"""

        tag_name = 'A Fish called Wanda'
        self.assertEqual(blog.models.Tag.objects.filter(name=tag_name).count(), 0)  # Check the tag does not exist

        self.cleese.tag_text=tag_name                                          # Add the tag
        tag = blog.models.Tag.objects.get(name =tag_name)
        self.assertEqual(tag.ref_count(), 1)
        self.cleese.tag_text=''                                                # Remove the tag
        self.assertEqual(blog.models.Tag.objects.filter(name=tag_name).count(), 0)  # Check the tag does not exist


    def test_025_042_TestTagDeletion(self):
        """Test that a tag is deleted when it is removed and the ref_count"""
        tag_name = 'A Fish called Wanda'
        tag = blog.models.Tag(name=tag_name)
        tag.save()

        self.assertEqual(tag.is_permanent, False)                               # Check the tag is temporary
        self.assertEqual(tag.ref_count(), 0)                                    # Check the tag does not exist

        self.cleese.tag_text=tag_name                                           # Add the tag to Mr Cleese

        self.assertEqual(tag.ref_count(), 1)

        self.cleese.tag_text=''                    # Remove the tag

        self.assertEqual(blog.models.Tag.objects.filter(name=tag_name).count(), 0)  # Check the tag does not exist


    def test_025_045_TestTagDeletionMultipleAdditions(self):
        """Test that a tag is deleted when it is removed and the ref_count"""
        tag_name = 'A Fish called Wanda'

        self.cleese.tag_text = tag_name                               # Add the tag to Messers Cleese & Palin
        self.palin.tag_text = tag_name

        tag = blog.models.Tag.objects.get(name =tag_name)
        self.assertEqual(tag.ref_count(), 2)                            # Check the tag exists
        self.cleese.tag_text=''                                         # Remove the tag from Cleese
        self.assertEqual(tag.ref_count(), 1)                            # Check the tag exists
        self.palin.tag_text= ''

        self.assertEqual(blog.models.Tag.objects.filter(name=tag_name).count(), 0)  # Check the tag does not exist

    def test_025_050_TestTagRetention(self):
        """Test that a permanent tag is retained when it is removed and the ref_count is zero"""

        self.assertEqual(self.python.is_permanent, True)     # Check the tag exists and is permanent
        self.cleese.tag_text=self.python.name                # Add the tag
        self.assertEqual(self.python.ref_count(), 1)         # Check the  ref count is incremented
        self.cleese.tag_text=''                              # Remove the tag
        self.assertEqual(self.python.ref_count(), 0)         # Check the tag still exists with a ref_count of zero
