from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from mysite.settings import EMAIL_HOST_USER


class CorrectAuthFlow(TestCase):
    def get_csrf_token(self, url) -> str:
        response = self.client.get(url)
        return response.cookies["csrftoken"].value

    def setUp(self) -> None:
        self.username = "testuser"
        self.password = "testpassword"
        self.email = "test@123"

        self.login_url = reverse("login:login")
        self.logout_url = reverse("login:logout")
        self.register_url = reverse("login:register")

        self.user = User.objects.create_user(
            username=self.username, password=self.password, email=self.email
        )

        self.client = Client(enforce_csrf_checks=True)

    def test_login_view(self) -> None:
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/login.html")

    def test_login_with_valid_credentials(self) -> None:
        response = self.client.post(
            self.login_url,
            {
                "username": self.username,
                "password": self.password,
                "csrfmiddlewaretoken": self.get_csrf_token(self.login_url),
            },
        )
        self.assertRedirects(response, reverse("login:dashboard"))

    def test_login_with_invalid_credentials(self) -> None:
        response = self.client.post(
            self.login_url,
            {
                "username": self.username,
                "password": "wrongpassword",
                "csrfmiddlewaretoken": self.get_csrf_token(self.login_url),
            },
            follow=True,
        )
        self.assertContains(response, "Invalid username or password.")
        self.assertTemplateUsed(response, "login/login.html")

    def test_logout_view(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, reverse("login:login"))

    def test_register_view(self) -> None:
        response = self.client.post(
            self.register_url,
            {
                "email": EMAIL_HOST_USER,
                "csrfmiddlewaretoken": self.get_csrf_token(self.register_url),
            },
            follow=True,
        )
        self.assertRedirects(response, reverse("login:register"))
        self.assertContains(response, "OTP sent to your email.")
        self.assertTemplateUsed(response, "login/register.html")
        self.assertTrue("email_otp_sent" in self.client.session)
        self.assertTrue("email" in self.client.session)
        self.assertTrue("otp" in self.client.session)

        otp = self.client.session.get("otp")

        response = self.client.post(
            self.register_url,
            {
                "username": "newuser",
                "otp": otp,
                "password": "newpassword",
                "confirm_password": "newpassword",
                "csrfmiddlewaretoken": self.get_csrf_token(self.register_url),
            },
            follow=True,
        )
        self.assertContains(
            response, "Registration successful. You can now log in."
        )
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertRedirects(response, reverse("login:login"))
        self.assertTemplateUsed(response, "login/login.html")
        self.assertFalse("email_otp_sent" in self.client.session)
        self.assertFalse("email" in self.client.session)
        self.assertFalse("otp" in self.client.session)
