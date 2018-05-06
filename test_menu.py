import unittest
import os
from datetime import datetime
import json
from app import create_app, db
from app.models import User, Menu, Meal

class MenuTestCase(unittest.TestCase):
    """This class represents the Menu test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client
        # meal1.save()
        # meal2.save()
        self.menu = {'meal_list': [1]}
        
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

    def test_non_admin_cannot_create_menu(self):
        """Test non-caterer cannot create a menu (POST request)"""
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('api/v1/menu/', headers=dict(Authorization="Bearer " + access_token), data=self.menu)
        expected = {"message": "You are unauthorized to access this"}
        result = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 401)
        self.assertEqual(result, expected)

    def test_admin_can_creates_menu(self):
        """Test admin can create a meal (POST request)"""
        result = self.login_admin()
        self.assertEqual(200, result.status_code)
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post('api/v1/menu/', headers=dict(Authorization="Bearer " + access_token), data=self.menu)
        expected = "Todays menu has been updated"
        result = json.loads(res.data.decode('utf-8'))['message']
        self.assertEqual(res.status_code, 201)
        self.assertEqual(result, expected)
        

    def test_user_can_access_menu(self):
        """Test user can access the menu (GET request)."""
        date = datetime.utcnow().date()
        menu = Menu(date=date)
        meal = Meal(name='Beef', description='Saucy beef', price=10)
        meal.save()
        menu.add_meal_to_menu(meal)
        menu.save()
        result = self.login_user()
        self.assertEqual(200, result.status_code)
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().get('api/v1/menu/', headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        self.assertEqual('Here is the menu for today', json.loads(res.data.decode('utf-8'))['message'])
        

    
    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            ##drop all tables
            db.session.remove()
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
