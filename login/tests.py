from unittest.mock import patch
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

    def test_login_page_valid_credentials(self):
        """
        Test that the login page works as intended.
        """
        response = self.client.post(
            reverse("login:login"),
            {"username": "testuser", "password": "testpassword"},
            follow=True,
        )
        self.assertRedirects(response, reverse("login:dashboard"))

    def test_login_page_invalid_credentials(self):
        """
        Test that the login page returns an error for invalid credentials.
        """
        response = self.client.post(
            reverse("login:login"),
            {"username": "testuser", "password": "wrongpassword"},
            follow=True,
        )
        self.assertContains(response, "Invalid username or password.")
        self.assertRedirects(response, reverse("login:login"))

    def test_login_redirects_to_dashboard(self):
        """
        Test that a successful login redirects to the dashboard.
        """
        response = self.client.post(
            reverse("login:login"),
            {"username": "testuser", "password": "testpassword"},
            follow=True,
        )
        self.assertRedirects(response, reverse("login:dashboard"))


class DashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email=EMAIL_HOST_USER,
            first_name="Test",
            last_name="User",
        )

    def test_dashboard_access(self):
        """
        Test that the dashboard is accessible to logged-in users.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse("login:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome back testuser")

    def test_dashboard_access_unauthenticated(self):
        """
        Test that the dashboard is not accessible to unauthenticated users.
        """
        response = self.client.get(reverse("login:dashboard"))
        self.assertRedirects(
            response,
            reverse("login:login") + "?next=" + reverse("login:dashboard"),
        )
        self.assertEqual(response.status_code, 302)

    def test_profile_page_access(self):
        """
        Test that the profile page is accessible to logged-in users.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse("login:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User Profile")


class RegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "username"
        self.password = "password"
        self.email = "test@user.com"

    def test_registration_page(self):
        """Test that the registration page loads correctly."""
        response = self.client.get(reverse("login:register"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Register")

    @patch("login.utils.email_utils.generate_otp", return_value="123456")
    def test_registration_with_valid_data(self, mock_generate_otp):
        """Test that a user can register with valid data."""
        response = self.client.post(
            reverse("login:register"),
            {
                "email": self.email,
            },
            follow=True,
        )
        self.assertRedirects(response, reverse("login:register"))
        self.assertContains(response, "OTP sent to your email.")

        response = self.client.post(
            reverse("login:register"),
            {
                "username": self.username,
                "password1": self.password,
                "password2": self.password,
                "otp": "123456",
            },
            follow=True,
        )
        self.assertRedirects(response, reverse("login:login"))
        self.assertContains(
            response, "Registration successful. You can now log in."
        )
        self.assertTrue(User.objects.filter(username=self.username).exists())
