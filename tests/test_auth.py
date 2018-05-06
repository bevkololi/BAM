import unittest
import json
from app import create_app, db

class AuthTestCase(unittest.TestCase):
    """Test case for the authentication blueprint."""

    def setUp(self):
        """Set up test variables."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.user_data = {
            'username': 'Bev Kololi',
            'email': 'bev@gmail.com',
            'password': 'pass1234'
        }

        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_registration(self):
        """Test user registration works correcty."""
        res = self.client().post('/auth/signup', data=self.user_data)
        self.assertEqual(res.status_code, 201)

        result = json.loads(res.data.decode('utf-8'))
        
    def test_already_registered_user(self):
        """Test that a user cannot be registered twice."""
        res = self.client().post('/auth/signup', data=self.user_data)
        self.assertEqual(res.status_code, 201)
        second_res = self.client().post('/auth/signup', data=self.user_data)
        self.assertEqual(second_res.status_code, 202)
        result = json.loads(second_res.data.decode())
        self.assertEqual(
            result['message'], "User already exists. Please login.")

    def test_user_login(self):
        """Test registered user can login."""
        res = self.client().post('/auth/signup', data=self.user_data)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/auth/login', data=self.user_data)
        result = json.loads(login_res.data.decode())
        self.assertEqual(result['message'], "You logged in successfully.")
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(result['access_token'])

    def test_non_registered_user_login(self):
        """Test non registered users cannot login."""
        not_a_user = {
            'username': 'Some guy',
            'email': 'not_a_user@example.com',
            'password': 'nope'
        }
        res = self.client().post('/auth/login', data=not_a_user)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 401)
        self.assertEqual(
            result['message'], "Invalid email or password, Please try again.")



if __name__ == "__main__":
    unittest.main()