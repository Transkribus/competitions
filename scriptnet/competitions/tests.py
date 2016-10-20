from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError

from .models import Affiliation, Competition, Individual
from .models import Track, Subtrack

from .evaluators import cmdline
from .evaluators import icfhr14_kws_tool, transkribusBaseLineMetricTool, transkribusErrorRate

def create_new_user():
    user = User.objects.create_user(
        username='sampleuser',
        password='mypassword',
        email='a@a.gr',
        first_name='John',
        last_name='Doe',
        )
    affiliation = Affiliation.objects.create(name='John Does university')
    user.individual.shortbio = 'This is the story of my life'
    user.individual.affiliations.add(affiliation)
    user.individual.save()
    return user

def create_competitions_tracks_subtracks(
        num_comps, 
        num_tracks_per_comp, 
        num_subtracks_per_track,
        sampledata_filename='test_private_data.txt',
        sampledata_filename_contents=b'This is test data',
    ):
    """
    A helper function that creates test competitions, tracks and subtracks.
    Creates a set number of competitions, then the given number of tracks per competition,
    and the given number of subtracks per track.
    """
    for cnum in range(1, num_comps+1):
        comp = Competition.objects.create(name='Competition {}'.format(cnum))
        print('Created {}'.format(comp))
        for tnum in range(1, num_tracks_per_comp+1):
            track = Track.objects.create(name='Track {}'.format(tnum), competition=comp)
            print('Created {}'.format(track))
            for snum in range(1, num_subtracks_per_track+1):
                subtrack = Subtrack.objects.create(
                    name='Subtrack {}'.format(snum), 
                    track=track,
                    private_data=SimpleUploadedFile(sampledata_filename, sampledata_filename_contents)
                ) #public_data=SimpleUploadedFile(sampledata_filename, sampledata_filename_contents),
                print('Created {}'.format(subtrack))

def show_all_competitions_tracks_subtracks():
    print(Competition.objects.all())
    print(Track.objects.all())
    print(Subtrack.objects.all())

class UrlTests(TestCase):
    """
    Check that the regexps in urls.py match to what we should expect
    """
    def test_regexp_index(self):
        a = reverse('index')
        self.assertEqual(a, '/competitions/')        

    def test_regexp_competitions_comp_track_subtrack(self):
        a = reverse('competition', kwargs = { 'competition_id': '1', 'track_id': '1', 'subtrack_id': '1', })
        self.assertEqual(a, '/competitions/1/1/1/')

    def test_regexp_competitions_comp_track(self):
        a = reverse('competition', kwargs = { 'competition_id': '1', 'track_id': '1', })
        self.assertEqual(a, '/competitions/1/1/')

    def test_regexp_competitions_comp(self):
        a = reverse('competition', kwargs = { 'competition_id': '1', })
        self.assertEqual(a, '/competitions/1/')

    def test_regexp_viewresults_comp_track_subtrack(self):
        a = reverse('viewresults', kwargs = {'competition_id': '1', 'track_id': '1', 'subtrack_id': '1',})
        self.assertEqual(a, '/competitions/1/1/1/viewresults/')

    def test_regexp_viewresults_comp_track(self):
        a = reverse('viewresults', kwargs = {'competition_id': '1', 'track_id': '1', })
        self.assertEqual(a, '/competitions/1/1/viewresults/')

    def test_regexp_viewresults_comp(self):
        a = reverse('viewresults', kwargs = {'competition_id': '1', })
        self.assertEqual(a, '/competitions/1/viewresults/')

class ViewForwardTests(TestCase):
    """
    Check that redirections work for various forms of given regexps.
    They should match those found at urls.py
    """
    def test_forward_index(self):
        response = self.client.get('/competitions/')
        self.assertEqual(response.status_code, 200)

    def test_forward_competitions_with_empty_dbase(self):
        response = self.client.get('/competitions/1/1/1/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/competitions/1/1/1')
        self.assertEqual(response.status_code, 301)
        response = self.client.get('/competitions/1/1/')
        self.assertEqual(response.status_code, 404)        
        response = self.client.get('/competitions/1/1')
        self.assertEqual(response.status_code, 301)        
        response = self.client.get('/competitions/1/')
        self.assertEqual(response.status_code, 404)        
        response = self.client.get('/competitions/1')
        self.assertEqual(response.status_code, 301)        

    def test_forward_competitions(self):
        create_competitions_tracks_subtracks(3, 3, 3)
        response = self.client.get('/competitions/1/')
        self.assertEqual(response.status_code, 200)        
        response = self.client.get('/competitions/1')
        self.assertEqual(response.status_code, 301)        
        response = self.client.get('/competitions/1/1/')
        self.assertEqual(response.status_code, 200)        
        response = self.client.get('/competitions/1/1')
        self.assertEqual(response.status_code, 301)                
        response = self.client.get('/competitions/1/1/1/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/competitions/1/1/1')
        self.assertEqual(response.status_code, 301)

class ViewReverseTests(TestCase):
    """
    Check that django.core.urlresolvers.reverse works
    for all views that reside in urls.py
    """
    def test_reverse_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_reverse_competition_with_empty_dbase_1(self):
        response = self.client.get(reverse('competition', 
            kwargs={
                'competition_id':'1', 
                'track_id':'1', 
                'subtrack_id':'1',
                }
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_reverse_competition_with_empty_dbase_2(self):
        response = self.client.get(reverse('competition', 
            kwargs={
                'competition_id':'2', 
                'track_id':'3', 
                'subtrack_id':'1',
                }
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_reverse_competition(self):
        create_competitions_tracks_subtracks(1, 2, 2)
        response = self.client.get(reverse('competition', 
            kwargs={
                'competition_id':'1', 
                'track_id':'2', 
                'subtrack_id':'1',
                }
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_reverse_viewresults_nosubmissions(self):
        """
        TODO: Do the same after having created some submissions
        """
        create_competitions_tracks_subtracks(1, 2, 2)
        response = self.client.get(reverse('viewresults', 
            kwargs={
                'competition_id':'1', 
                'track_id':'2', 
                'subtrack_id':'1',
                }
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_reverse_scoreboard_nosubmissions(self):
        """
        TODO: Do the same after having created some submissions
        """        
        create_competitions_tracks_subtracks(1, 2, 2)
        response = self.client.get(reverse('scoreboard', 
            kwargs={
                'competition_id':'1', 
                }
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_reverse_submit(self):
        create_competitions_tracks_subtracks(1, 2, 2)
        response = self.client.get(reverse('submit', 
            kwargs={
                'competition_id':'1', 
                'track_id':'2', 
                'subtrack_id':'1',                
                }
            )
        )
        self.assertEqual(response.status_code, 200)        
    

class ModelTests(TestCase):
    def test_affiliation_creation(self):
        """
        Create an affiliation and test that it appears
        on the master page -- should reside in one of 
        the buttons of the register block
        """
        testname = 'Test affiliation'
        w = Affiliation.objects.create(name=testname)
        response = self.client.get(reverse('index'))
        self.assertContains(response, testname)

    def test_competition_creation(self):
        """
        Create a competition and test that it appears
        on the master page -- there is a special block 
        that shows all competitions
        """
        testname = 'Test competition'
        w = Competition.objects.create(name=testname)
        response = self.client.get(reverse('index'))
        self.assertContains(response, testname)
    
    def test_track_uniquepercomp_ids(self):
        """
        Check that all track 'unique per competition ids' are indeed unique
        """
        num_comps = 3
        num_tracks = 3
        create_competitions_tracks_subtracks(num_comps, num_tracks, 0)
        self.assertEqual(len(Track.objects.all()), num_comps*num_tracks)
        for t in Track.objects.all():
            my_id = t.percomp_uniqueid
            my_competition = t.competition
            self.assertEqual(len(Track.objects.filter(competition=my_competition).filter(percomp_uniqueid=my_id)), 1)

    def test_subtrack_uniquepercomp_ids(self):
        """
        Check that all subtrack 'unique per competition ids' are indeed unique
        """
        num_comps = 2
        num_tracks = 2
        num_subtracks = 5
        create_competitions_tracks_subtracks(num_comps, num_tracks, num_subtracks)
        self.assertEqual(len(Subtrack.objects.all()), num_comps*num_tracks*num_subtracks)
        for st in Subtrack.objects.all():
            my_id = st.pertrack_uniqueid
            my_track = st.track
            self.assertEqual(len(Subtrack.objects.filter(track=my_track).filter(pertrack_uniqueid=my_id)), 1)
    
    def test_subtrack_files(self):
        """
        Check public/private files functionality is ok.
        Check that data work if they are either uncompressed or compressed.
        """
        self.assertEqual(1, 1)

    def test_user_creation(self):
        """
        Creation of a user should automatically create an 'Individual',
        since Individual is on a 1-1 relationship with User, ie it is
        a 'User profile'.
        """
        testname = 'Test user'
        w = User.objects.create_user(username=testname)
        q = User.objects.get(username=testname)
        self.assertEqual(w, q)
        iq = Individual.objects.all()
        self.assertEqual(len(iq), 1)

class EvaluatorTests(TestCase):
    def test_icfhr14_kws_tool(self):
        res = icfhr14_kws_tool()
        self.assertEqual(res, {
            'pr-curve': '["1.0000", "1.0000", "1.0000", "1.0000", "1.0000", "0.6667", "0.0000", "0.0000", "0.0000", "0.0000", "0.0000"]',
            'p@5': '0.9000',
            'r-precision': '0.5000',
            'map': '0.5185',
            'ndcg': '0.6395',
            'p@10': '0.5000',
            'ndcg-binary': '0.6817'
            }
        )
    def test_transkribusBaseLineMetricTool(self):
        res = transkribusBaseLineMetricTool()
        self.assertEqual(res, {
                'bl-avg-precision': '0.744',
                'bl-avg-recall': '0.7586',
                'bl-avg-fmeasure': '0.7512',
            }
        )


class TranskribusErrorRateTests(TestCase):
    def _test_transkribuserrorrate(self, params="", tgt={}):
        res = transkribusErrorRate(privatedata="competitions/executables/TranskribusErrorRate/testresources/gt.tgz",
                                   resultdata="competitions/executables/TranskribusErrorRate/testresources/hyp.tgz",
                                   tmpfolder="competitions/executables/TranskribusErrorRate/testresources/tmp",
                                   execpath="competitions/executables/TranskribusErrorRate/", params=params)
        print("output of test is '" + str(res) + "'.")
        print("output of tgt  is '" + str(tgt) + "'.")
        for key in tgt:
            self.assertEqual(float(tgt.get(key)), float(res.get(key)))

    def test_transkribuserrorrate_cer(self):
        self._test_transkribuserrorrate(
            params="",
            tgt={
                'DEL': '0.05',
                'ERR': '0.465',
                'SUB': '0.215',
                'INS': '0.2'
            })

    def test_transkribuserrorrate_wer(self):
        self._test_transkribuserrorrate(
            params="-w",
            tgt={
                'DEL': '0.1',
                'ERR': '0.78',
                'SUB': '0.3',
                'INS': '0.38',
            })

    def test_transkribuserrorrate_cer_upper(self):
        self._test_transkribuserrorrate(
            params="-u",
            tgt={
                'DEL': '0.05',
                'ERR': '0.335',
                'SUB': '0.085',
                'INS': '0.2',
            })

    def test_transkribuserrorrate_wer_letter(self):
        self._test_transkribuserrorrate(
            params="-l -w",
            tgt={
                'DEL': '0.02',
                'ERR': '0.74',
                'SUB': '0.32',
                'INS': '0.4',
            })


class AuthenticationTests(TestCase):
    """
    Here, register and login using the backend solely.
    In this sense, these tests are complementary with FormTests
    that should test register, login and submit on the frontend.
    """
    def test_register_user(self):
        user = create_new_user()
        self.assertIsNotNone(user)
        self.assertEqual(len(User.objects.all()), 1)
        self.assertEqual(len(Individual.objects.all()), 1)
        self.assertEqual(user.first_name, 'John')

    def test_register_existing_user(self):
        """
        Register with a username that already exists.
        This should throw an IntegrityError
        """
        user = create_new_user()
        try:
            user2 = create_new_user()
        except(IntegrityError):
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def test_login_unknown_user(self):
        self.assertFalse(self.client.login(username='temporary', password='temporary'))

    def test_login_bad_password(self):
        create_new_user()
        self.assertTrue(User.objects.all()[0].username, 'sampleuser')
        self.assertFalse(self.client.login(username='sampleuser', password='badpassword'))

    def test_user_creation_and_login(self):
        create_new_user()
        self.assertTrue(User.objects.all()[0].username, 'sampleuser')
        self.assertTrue(self.client.login(username='sampleuser', password='mypassword'))
    
class FormTests(TestCase):
    def test_registerform(self):
        self.assertEqual(1, 1)
    def test_registerform_existinguser(self):
        self.assertEqual(1, 1)
    def test_loginform(self):
        self.assertEqual(1, 1)
    def test_submitresultform(self):
        self.assertEqual(1, 1)

class ThirdpartyTests(TestCase):
    def test_p7zip(self):
        self.assertIn('p7zip Version', cmdline('7zr'))
