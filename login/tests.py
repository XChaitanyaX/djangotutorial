from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from mysite.settings import EMAIL_HOST_USER


class LoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email=EMAIL_HOST_USER,
            first_name="Test",
            last_name="User",
        )

    def test_valid_credentials(self):
        """
        Test that a user can log in with valid credentials.
        """
        is_valid_cred = self.client.login(
            username="testuser", password="testpassword"
        )
        self.assertTrue(is_valid_cred)

    def test_invalid_credentials(self):
        is_valid_cred = self.client.login(username="user", password="password")
        self.assertFalse(is_valid_cred)
