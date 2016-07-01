from django.test import TestCase, Client, LiveServerTestCase
from django.utils import timezone
from django.contrib.auth.models import User

# Create your tests here.

#Add a test to ...
#TODO: check if the functions in evaluator.py all correspond to benchmark model elements and vice versa

#TODO: check that all available benchmarks run, and that they give the results that is expected for a preset dataset.

#TODO: login a user and log him out

class AdminTest(LiveServerTestCase):
 
    def setUp(self):
        self.client = Client()

    def test_login(self):
        # Get login page
        response = self.client.get('/admin/login')

        # Check response code
        self.assertEquals(response.status_code, 301)

        # Check 'Log in' in response
        self.assertTrue('Log in' in response.content)

        # Log the user in
        self.client.login(username='XXX', password="XXX")

        # Check response code
        response = self.client.get('/admin/login')
        self.assertEquals(response.status_code, 200)

        # Check 'Log out' in response
        self.assertTrue('Log out' in response.content)

    def test_logout(self):
        # Log in
        self.client.login(username='XXX', password="XXX")

        # Check response code
        response = self.client.get('/admin/logout')
        self.assertEquals(response.status_code, 301)

        # Check 'Log out' in response
        self.assertTrue('Log out' in response.content)

        # Log out
        self.client.logout()

        # Check response code
        response = self.client.get('/admin/logout')
        self.assertEquals(response.status_code, 200)

        # Check 'Log in' in response
        self.assertTrue('Log in' in response.content)

#TODO: register a new user and delete him


