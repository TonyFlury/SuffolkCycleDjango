from django.test import TestCase

# Test only the home root - don't test the individual app urls


class BasicUnauthenticatedUrl(TestCase):
    """ Base test cases to check that all the primary expected urls respond.is a 200 status code
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_000_00010_test_home_200(self):
        pass

    def test_000_00020_test_readmore_200(self):
        pass

    def test_000_00030_test_getinvolved_200(self):
        pass

    def test_000_00040_test_signin_200(self):
        pass

    def test_000_00050_test_SponsorUs_200(self):
        pass

    def test_000_00060_test_blog_200(self):
        pass

