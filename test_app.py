import unittest
from app import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        # Register the test user before running the login test
        self.app.post('/register', json={"username": "testuser", "password": "testpassword"})

    def test_register(self):
        # Test user registration
        response = self.app.post('/register', json={"username": "testuser2", "password": "testpassword2"})
        self.assertEqual(response.status_code, 201)

    def test_login(self):
        # Test user login
        response = self.app.post('/login', json={"username": "testuser", "password": "testpassword"})
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()