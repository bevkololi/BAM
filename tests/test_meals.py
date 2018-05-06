import unittest
import os
import json
from . import create_app, db
from . import User

class MealTestCase(unittest.TestCase):
    """This class represents the Meal test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client
        self.meal = {'name': 'Ugali and sukuma wiki', 'description': 'This is ugali description', 'price': 20}

        
        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

    def register_user(self, username= 'Some user', email="user@gmail.com", password="pass1234"):
        user_data = {
            'username': username,
            'email': email,
            'password': password,
        }
        return self.client().post('/auth/signup', data=user_data)

    def login_user(self, username= 'Some user', email="user@gmail.com", password="pass1234"):
        user = User(username=username, email=email, password=password)
        user.save()
        user_data = {
            'username': username,
            'email': email,
            'password': password,
        }
        return self.client().post('/auth/login', data=user_data)

    def login_admin(self, username= 'Some user', email="user@gmail.com", password="pass1234", caterer=True):
        admin = User(username=username, email=email, password=password)
        admin.caterer =caterer
        admin.save()
        user_data = {
            'username': username,
            'email': email,
            'password': password,
            'caterer': True
        }
        return self.client().post('/auth/login', data=user_data)

    def test_non_admin_cannot_create_meals(self):
        """Test that a non-caterer cannot create a meal (POST request)"""
        # self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('api/v1/meals/', headers=dict(Authorization="Bearer " + access_token), data=self.meal)
        expected = {"message": "You are unauthorized to access this"}
        result = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 401)
        self.assertEqual(result, expected)

    def test_admin_can_creates_meals(self):
        """Test caterer can create a meal (POST request)"""
        result = self.login_admin()
        self.assertEqual(200, result.status_code)
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('api/v1/meals/', headers=dict(Authorization="Bearer " + access_token), data=self.meal)
        expected = 'Meal created successfully'
        result = json.loads(res.data.decode('utf-8'))['message']
        self.assertEqual(res.status_code, 201)
        self.assertEqual(result, expected)
        

    def test_non_admin_cannot_get_meals(self):
        """Test non-caterer cannot get mealss (GET request)."""
        # self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('api/v1/meals/', headers=dict(Authorization="Bearer " + access_token), data=self.meal)
        self.assertEqual(res.status_code, 401)
        res = self.client().get('api/v1/meals/', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        

    def test_admin_can_get_meals(self):
        """Test caterer can get a meal (GET request)."""
        result = self.login_admin()
        self.assertEqual(200, result.status_code)
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('api/v1/meals/', headers=dict(Authorization="Bearer " + access_token), data=self.meal)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('api/v1/meals/', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)

    def test_non_admin_cannot_manpulate_meal(self):
        """Test non-caterer cannot get a single meal by using it's id."""
        # self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post('api/v1/meals/', headers=dict(Authorization="Bearer " + access_token), data=self.meal)
        self.assertEqual(rv.status_code, 401)
        results = json.loads(rv.data.decode())
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/api/v1/meals/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 401)

    def test_admin_can_manpulate_meal(self):
        """Test caterer can get a single meal by using it's id."""
        result = self.login_admin()
        self.assertEqual(200, result.status_code)
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post('api/v1/meals/', headers=dict(Authorization="Bearer " + access_token), data=self.meal)
        self.assertEqual(rv.status_code, 201)
        results = json.loads(rv.data.decode())
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/api/v1/meals/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 200)
        

    def test_non_admin_cannot_edit_meals(self):
        """Test non-admin cannot edit an existing meal. (PUT request)"""
        # self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            'api/v1/meals/', headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Spaghetti and rice', 'description': 'This is a description of ugali and sukuma wiki', 'price': 40})
        self.assertEqual(rv.status_code, 401)
        rv = self.client().put(
            'api/v1/meals/1', headers=dict(Authorization="Bearer " + access_token),
            data={
                'name': 'Spaghetti and rice and stewed meat', 'description': 'This is a description of ugali and sukuma wiki', 'price': 40
            })
        self.assertEqual(rv.status_code, 401)
        results = self.client().get('api/v1/meals/1', headers=dict(Authorization="Bearer " + access_token))


    def test_admin_can_edit_meals(self):
        """Test admin can edit an existing meal. (PUT request)"""
        result = self.login_admin()
        self.assertEqual(200, result.status_code)
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            'api/v1/meals/', headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Spaghetti and rice', 'description': 'This is a description of ugali and sukuma wiki', 'price': 40})
        self.assertEqual(rv.status_code, 201)
        rv = self.client().put(
            'api/v1/meals/1', headers=dict(Authorization="Bearer " + access_token),
            data={
                'name': 'Spaghetti and rice and stewed meat', 'description': 'This is a description of ugali and sukuma wiki', 'price': 40
            })
        self.assertEqual(rv.status_code, 200)
        results = self.client().get('api/v1/meals/1', headers=dict(Authorization="Bearer " + access_token))
        

    def test_no_admin_canoot_delete_meal(self):
        """Test non-caterer cannot delete an existing meal. (DELETE request)."""
        # self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            'api/v1/meals/', headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Spaghetti and rice', 'description': 'This is a description of ugali and sukuma wiki', 'price': 40})
        self.assertEqual(rv.status_code, 401)
        res = self.client().delete('api/v1/meals/1', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 401)
        result = self.client().get('api/v1/meals/1', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 401)

    def test_admin_can_delete_meal(self):
        """Test caterer can delete an existing meal. (DELETE request)."""
        result = self.login_admin()
        self.assertEqual(200, result.status_code)
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            'api/v1/meals/', headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Spaghetti and rice', 'description': 'This is a description of ugali and sukuma wiki', 'price': 40})
        self.assertEqual(rv.status_code, 201)
        res = self.client().delete('api/v1/meals/1', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        result = self.client().get('api/v1/meals/1', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
