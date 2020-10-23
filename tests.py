import os
import unittest
import json
from dotenv import load_dotenv
from app import app
from models import db

unittest.TestLoader.sortTestMethodsUsing = None


class CastingCapstoneTestCase(unittest.TestCase):

    actor_id = 1
    movie_id = 1

    # custom lambda helper functions
    check_success = lambda self, response, data: response.status_code == 200 and data['success']
    check_bad_request = lambda self, response, data: response.status_code == 400 and not data['success']
    check_auth_error = lambda self, response, data: response.status_code == 401 and not data['success']
    check_not_found = lambda self, response, data: response.status_code == 404 and not data['success']
    check_unprocessable = lambda self, response, data: response.status_code == 422 and not data['success']

    def request(self, url, method, token, data=None):
        res = method(url, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + str(token)},
                     json=data)
        return res, json.loads(res.data)

    def setUp(self):
        """Define test variables and initialize app."""
        load_dotenv()
        self.casting_assistent_token = os.getenv('CASTING_ASSISTANT')
        self.casting_director_token = os.getenv('CASTING_DIRECTOR')
        self.casting_producer_token = os.getenv('CASTING_PRODUCER')
        self.app = app
        self.client = self.app.test_client()

        # binds the app to the current context
        with self.app.app_context():
            db.create_all()

        self.new_movie = {
            'title': 'Supermen',
            'release_date': '12.02.2014'
        }
        self.new_actor = {
            'name': 'Alex Born',
            'age': 32,
            'gender': 'Male'
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test00_get_actors(self):
        res, data = self.request('/actors', self.client.get, self.casting_assistent_token)
        self.assertTrue(self.check_success(res, data))

    def test01_get_actors_err(self):
        res, data = self.request('/actors', self.client.get, self.casting_assistent_token + 'err')
        self.assertTrue(self.check_auth_error(res, data))

    def test02_post_actors(self):
        res, data = self.request('/actors', self.client.post, self.casting_director_token, self.new_actor)
        self.__class__.actor_id = data['actor']['id']
        self.assertTrue(self.check_success(res, data))

    def test03_post_actors_err(self):
        res, data = self.request('/actors', self.client.post, self.casting_assistent_token, self.new_actor)
        self.assertTrue(self.check_auth_error(res, data))

    def test04_patch_actors(self):
        self.new_actor['name'] = 'UPD Alex'
        res, data = self.request(f'/actors/{self.__class__.actor_id}', self.client.patch, self.casting_director_token,
                                 self.new_actor)
        self.assertTrue(self.check_success(res, data))

    def test05_patch_actors_err(self):
        res, data = self.request(f'/actors/{self.__class__.actor_id}', self.client.patch, self.casting_assistent_token,
                                 self.new_actor)
        self.assertTrue(self.check_auth_error(res, data))

    def test06_delete_actors(self):
        res, data = self.request(f'/actors/{self.__class__.actor_id}', self.client.delete, self.casting_director_token)
        self.assertTrue(self.check_success(res, data))

    def test07_delete_actors_err(self):
        res, data = self.request(f'/actors/{self.__class__.actor_id}', self.client.patch, self.casting_assistent_token)
        self.assertTrue(self.check_auth_error(res, data))

    def test08_get_movies(self):
        res, data = self.request('/movies', self.client.get, self.casting_assistent_token)
        self.assertTrue(self.check_success(res, data))

    def test09_get_movies_err(self):
        res, data = self.request('/movies', self.client.get, self.casting_assistent_token + 'err')
        self.assertTrue(self.check_auth_error(res, data))

    def test10_post_movies(self):
        res, data = self.request('/movies', self.client.post, self.casting_producer_token, self.new_movie)
        self.__class__.movie_id = data['movie']['id']
        self.assertTrue(self.check_success(res, data))

    def test11_post_movies_err(self):
        res, data = self.request('/movies', self.client.post, self.casting_director_token, self.new_movie)
        self.assertTrue(self.check_auth_error(res, data))

    def test12_patch_movies(self):
        self.new_movie['title'] = 'UPD Supermen'
        res, data = self.request(f'/movies/{self.__class__.movie_id}', self.client.patch, self.casting_director_token,
                                 self.new_movie)
        self.assertTrue(self.check_success(res, data))

    def test13_patch_movies_err(self):
        res, data = self.request(f'/movies/{self.__class__.movie_id}', self.client.patch, self.casting_assistent_token,
                                 self.new_movie)
        self.assertTrue(self.check_auth_error(res, data))

    def test14_delete_movies(self):
        res, data = self.request(f'/movies/{self.__class__.movie_id}', self.client.delete, self.casting_producer_token)
        self.assertTrue(self.check_success(res, data))

    def test15_delete_movies_err(self):
        res, data = self.request(f'/movies/{self.__class__.movie_id}', self.client.patch, self.casting_assistent_token)
        self.assertTrue(self.check_auth_error(res, data))


if __name__ == "__main__":
    unittest.main()
