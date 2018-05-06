import unittest
import os
import json
from app import create_app, db
from app.models import User

class UserTestCase(unittest.TestCase):
    """This class represents the Meal test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client
        self.user = {'username': 'Joseph Joe', 'email': 'joe@gmail.com', 'password': 'pass1234', 'caterer':False}

        
        with self.app.app_context():
            #create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def register_user(self, username= 'Some user', email="user@gmail.com", password="pass1234"):
        user_data = {
            'username': username,
            'email': email,
            'password': password,
        }
        user = User(username=username, email=email, password=password)
        user.save()
  
        return None #self.client().post('/auth/signup', data=user_data)

    def login_user(self, username= 'Some user', email="user@gmail.com", password="pass1234"):
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

    

    def test_admin_can_manpulate_users(self):
        """Test API can get a single meal by using it's id."""
        result = self.login_admin()
        self.assertEqual(200, result.status_code)
        access_token = json.loads(result.data.decode())['access_token']
        result = self.client().get(
            '/api/v1/users/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 200)   

    
    def test_admin_can_delete_user(self):
        """Test API can delete an existing meal. (DELETE request)."""
        user = User(username='pp', email='pp@m', password='12334455')
        user.save()
        result = self.login_admin()
        self.assertEqual(200, result.status_code)
        access_token = json.loads(result.data.decode())['access_token']
        result = self.client().get(
            '/api/v1/users/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 200)
        res = self.client().delete('api/v1/users/1', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        result = self.client().get('api/v1/users/1', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)


    def test_admin_can_promote_users(self):
        """Test admin can promote a user (PUT request)."""
        result = self.login_admin()
        self.assertEqual(200, result.status_code)
        access_token = json.loads(result.data.decode())['access_token']
        result = self.client().put(
            '/api/v1/promote/user/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 200) 

    def test_nonuser_can_promote_users(self):
        """Test non-caterer cannot promote user (PUT request)."""
        self.register_user()
        result = self.login_user()
        self.assertEqual(200, result.status_code)
        access_token = json.loads(result.data.decode())['access_token']
        result = self.client().put(
            '/api/v1/promote/user/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 401) 

    def test_admin_can_edit_user(self):
        """Test admin can edit existing user. (PUT request)"""
        user = User(username='pp', email='pp@m', password='12334455')
        user.save()
        result = self.login_admin()
        self.assertEqual(200, result.status_code)
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().put(
            'api/v1/users/1', headers=dict(Authorization="Bearer " + access_token),
            data={
                'username': 'Sharon', 'email': 'sharon@gmail.com', 'password': 'pass1234'
            })
        self.assertEqual(rv.status_code, 200)
        results = self.client().get('api/v1/users/1', headers=dict(Authorization="Bearer " + access_token))

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            ##drop all tables
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
