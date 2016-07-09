from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from .models import Affiliation, Competition, Individual

class ModelTests(TestCase):
    def test_affiliation_creation(self):
        testname = 'Test affiliation'
        w = Affiliation.objects.create(name=testname)
        response = self.client.get(reverse('index'))
        self.assertContains(response, testname)

    def test_competition_creation(self):
        testname = 'Test competition'
        w = Competition.objects.create(name=testname)
        response = self.client.get(reverse('index'))
        self.assertContains(response, testname)

    def test_user_creation(self):
        """
        Creation of a user should automatically create an 'Individual'
        """
        testname = 'Test user'
        w = User.objects.create_user(username=testname)
        q = User.objects.get(username=testname)
        self.assertEqual(w, q)
        iq = Individual.objects.all()
        self.assertEqual(len(iq), 1)

    def test_user_creation_and_login(self):
        """
        Create a user and authenticate him
        """
        self.assertEqual(1, 1)

class EvaluatorTests(TestCase):
    #TODO: check that all available benchmarks run, and that they give 
    # the results that is expected for a preset dataset.
    def test_evaluator_prwto(self):
        self.assertEqual(1, 1)

class ViewTests(TestCase):
    def test_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        #self.assertIn(w.title, resp.content)
        #self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_competitions_when_there_are_none(self):
        response = self.client.get(reverse('competition'), 
            kwargs={
                'competition_id':'10', 
                'track_id':'1', 
                'subtrack_id':'1',
                })        
        #reverse('viewresults', args=(competition_id, track_id, subtrack_id,))
        self.assertEqual(response.status_code, 404)

class AuthenticationTests(TestCase):
    def test_register(self):
        #TODO: register a new user and delete him
        self.assertEqual(1, 1)
    def test_login_valid_user(self):
        #Login with an existing user
        self.assertEqual(1, 1)
    def test_login_unknown_user(self):
        #Login with an invalid user
        self.assertEqual(1, 1)        
    def test_register_and_login(self):
        self.assertEqual(1, 1)

class FormTests(TestCase):
    def test_registerform(self):
        self.assertEqual(1, 1)
    def test_loginform(self):
        self.assertEqual(1, 1)
    def test_submitresultform(self):
        self.assertEqual(1, 1)