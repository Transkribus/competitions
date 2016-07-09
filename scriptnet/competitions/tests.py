from django.test import TestCase

class ModelTests(TestCase):
    def test_affiliation_prwto(self):
        self.fail("This test is under construction.")

    def test_affiliation_deutero(self):
        self.fail("This test is under construction.")

class EvaluatorTests(TestCase):
    #TODO: check that all available benchmarks run, and that they give the results that is expected for a preset dataset.
    def test_evaluator_prwto(self):
        self.assertEqual(1, 1)

class ViewTests(TestCase):
    def test_index(self):
        self.fail("This test is under construction")

class AuthenticationTests(TestCase):
    def test_register(self):
        #TODO: register a new user and delete him    
        self.fail("This test is under construction")
    def test_login_valid_user(self):
        #Login with an existing user
        self.assertEqual(1, 1)
    def test_login_unknown_user(self):
        #Login with an invalid user
        self.assertEqual(1, 1)        
    def test_register_and_login(self):
        self.fail("This test is under construction")

class FormTests(TestCase):
    def test_registerform(self):
        self.fail("")
    def test_loginform(self):
        self.fail("")
    def test_submitresultform(self):
        self.fail("")