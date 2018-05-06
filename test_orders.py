import unittest
import os
import json
from app import create_app, db
from app.models import User

class OrderTestCase(unittest.TestCase):
    """This class represents the Order test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client
        self.order = {'meal': 'Ugali and sukuma wiki', 'quantity':2}

        
        with self.app.app_context():
            #create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def register_user(self, username= 'Some user', email="user@gmail.com", password="pass1234"):
        user_data = {
            'username': username,
            'email': email,
            'password': password
        }
        user = User(username=username, email=email, password=password)
        user.save()
  
        return None #self.client().post('/auth/signup', data=user_data)

    def login_user(self, username= 'Some user', email="user@gmail.com", password="pass1234"):
        # user = User(username=username, email=email, password=password)
        # user.save()
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

    def test_non_admin_can_create_order(self):
        """Test user can create an order (POST request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('api/v1/myorders/', headers=dict(Authorization="Bearer " + access_token), data=self.order)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Ugali', str(res.data))

    def test_user_can_see_their_orders(self):
        """Test user can get their order history (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('api/v1/myorders/', headers=dict(Authorization="Bearer " + access_token), data=self.order)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('api/v1/myorders/', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        self.assertIn('Ugali', str(res.data))

    def test_admin_can_get_orders(self):
        """Test admin can get all orders (GET request)."""
        result = self.login_admin()
        self.assertEqual(200, result.status_code)
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().get('api/v1/orders/', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)

    def test_admin_can_manpulate_order(self):
        """Test admin can get a single order by using it's id."""
        result = self.login_admin()
        self.assertEqual(200, result.status_code)
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post('api/v1/orders/', headers=dict(Authorization="Bearer " + access_token), data=self.order)
        self.assertEqual(rv.status_code, 201)
        results = json.loads(rv.data.decode())
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/api/v1/orders/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 200)

    def test_non_admin_cannot_manpulate_order(self):
        """Test non_caterer cannot get a single meal by using it's id."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post('api/v1/orders/', headers=dict(Authorization="Bearer " + access_token), data=self.order)
        self.assertEqual(rv.status_code, 401)
        results = json.loads(rv.data.decode())
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/api/v1/orders/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 401)
        

    def test_order_can_be_edited(self):
        """Test caterer can edit an existing order. (PUT request)"""
        result = self.login_admin()
        self.assertEqual(200, result.status_code)
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            'api/v1/orders/', headers=dict(Authorization="Bearer " + access_token),
            data={'meal': 'Spaghetti and rice', 'quantity': 3})
        self.assertEqual(rv.status_code, 201)
        rv = self.client().put(
            'api/v1/orders/1', headers=dict(Authorization="Bearer " + access_token),
            data={
                'meal': 'Spaghetti and rice and stewed meat', 'quantity': 2
            })
        self.assertEqual(rv.status_code, 200)
        results = self.client().get('api/v1/orders/1', headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('stewed meat', str(results.data))

    def test_order_deletion_by_admin(self):
        """Test caterer can delete an existing order. (DELETE request)."""
        result = self.login_admin()
        self.assertEqual(200, result.status_code)
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            'api/v1/orders/', headers=dict(Authorization="Bearer " + access_token),
            data={'meal': 'Spaghetti and rice', 'quantity': 3})
        self.assertEqual(rv.status_code, 201)
        res = self.client().delete('api/v1/orders/1', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        result = self.client().get('api/v1/orders/1', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)

    def test_non_admin_cannot_delete_order(self):
        """Test non_caterer cannot delete an existing order. (DELETE request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            'api/v1/orders/', headers=dict(Authorization="Bearer " + access_token),
            data={'meal': 'Spaghetti and rice', 'quantity': 3})
        self.assertEqual(rv.status_code, 401)
        res = self.client().delete('api/v1/orders/1', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 401)
        result = self.client().get('api/v1/orders/1', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 401)



    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
