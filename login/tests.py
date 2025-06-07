from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from unittest.mock import patch


# Shared mixins and base classes for DRY tests
class AuthTestMixin:
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        self.email = "test@123.com"
        self.user = User.objects.create_user(
            username=self.username, password=self.password, email=self.email
        )
        self.client = Client(enforce_csrf_checks=True)
        self.login_url = reverse("login:login")
        self.logout_url = reverse("login:logout")
        self.register_url = reverse("login:register")
        self.dashboard_url = reverse("login:dashboard")

    def get_csrf(self, url):
        return self.client.get(url).cookies["csrftoken"].value


class ProfileTestMixin:
    def setUp(self):
        self.username = "profileuser"
        self.password = "profilepass"
        self.email = "profile@user.com"
        self.user = User.objects.create_user(
            username=self.username, password=self.password, email=self.email
        )
        self.client = Client()
        self.login_url = reverse("login:login")
        self.dashboard_url = reverse("login:dashboard")
        self.profile_url = reverse("login:profile")
        self.update_profile_url = reverse("login:update_profile")
        self.reset_password_url = reverse("login:reset_password")
        self.verify_otp_url = reverse("login:verify_otp")

    def login(self):
        self.client.login(username=self.username, password=self.password)


# Auth Views Tests
class TestLoginView(AuthTestMixin, TestCase):
    def test_get_login(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/login.html")

    def test_post_valid_login(self):
        response = self.client.post(
            self.login_url,
            {
                "username": self.username,
                "password": self.password,
                "csrfmiddlewaretoken": self.get_csrf(self.login_url),
            },
        )
        self.assertRedirects(response, self.dashboard_url)

    def test_post_invalid_login(self):
        response = self.client.post(
            self.login_url,
            {
                "username": self.username,
                "password": "wrong",
                "csrfmiddlewaretoken": self.get_csrf(self.login_url),
            },
            follow=True,
        )
        self.assertContains(response, "Invalid username or password.")
        self.assertTemplateUsed(response, "login/login.html")

    def test_post_invalid_form(self):
        response = self.client.post(
            self.login_url,
            {"csrfmiddlewaretoken": self.get_csrf(self.login_url)},
            follow=True,
        )
        self.assertContains(response, "Invalid form submission.")
        self.assertTemplateUsed(response, "login/login.html")


class TestLogoutView(AuthTestMixin, TestCase):
    def test_logout_redirects(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)


class TestRegisterView(AuthTestMixin, TestCase):
    def test_get_register_email(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/register.html")
        self.assertIn("form", response.context)

    def test_post_invalid_email(self):
        response = self.client.post(
            self.register_url,
            {
                "email": "notanemail",
                "csrfmiddlewaretoken": self.get_csrf(self.register_url),
            },
            follow=True,
        )
        self.assertContains(response, "Invalid email address.")
        self.assertTemplateUsed(response, "login/register.html")

    def test_post_valid_email(self):
        with patch(
            "login.utils.email_utils.send_verification_otp_email",
            return_value=True,
        ):
            response = self.client.post(
                self.register_url,
                {
                    "email": "new@user.com",
                    "csrfmiddlewaretoken": self.get_csrf(self.register_url),
                },
                follow=True,
            )
            self.assertRedirects(response, self.register_url)
            self.assertContains(response, "OTP sent to your email.")
            self.assertTemplateUsed(response, "login/register.html")
            self.assertIn("email", self.client.session)


class TestUserRegistrationView(AuthTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.session = self.client.session
        self.session["email_otp_sent"] = True
        self.session["otp"] = "123456"
        self.session["email"] = "new@user.com"
        self.session.save()

    def test_post_invalid_method(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        # Should render registration form, not redirect

    def test_post_invalid_otp(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "newuser",
                "otp": "wrong",
                "password": "pass",
                "confirm_password": "pass",
                "csrfmiddlewaretoken": self.get_csrf(self.register_url),
            },
            follow=True,
        )
        self.assertContains(response, "Invalid OTP.")
        self.assertTemplateUsed(response, "login/register.html")

    def test_post_username_exists(self):
        response = self.client.post(
            self.register_url,
            {
                "username": self.username,
                "otp": "123456",
                "password": "pass",
                "confirm_password": "pass",
                "csrfmiddlewaretoken": self.get_csrf(self.register_url),
            },
            follow=True,
        )
        self.assertContains(response, "Username already exists.")
        self.assertTemplateUsed(response, "login/register.html")

    def test_post_password_mismatch(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "newuser",
                "otp": "123456",
                "password": "pass1",
                "confirm_password": "pass2",
                "csrfmiddlewaretoken": self.get_csrf(self.register_url),
            },
            follow=True,
        )
        self.assertContains(
            response, "Registration failed. Please check your details."
        )
        self.assertTemplateUsed(response, "login/register.html")

    def test_post_success(self):
        response = self.client.post(
            self.register_url,
            {
                "username": "newuser",
                "otp": "123456",
                "password": "pass",
                "confirm_password": "pass",
                "csrfmiddlewaretoken": self.get_csrf(self.register_url),
            },
            follow=True,
        )
        self.assertContains(
            response, "Registration successful. You can now log in."
        )
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertRedirects(response, self.login_url)
        self.assertTemplateUsed(response, "login/login.html")


# Profile Views Tests
class TestDashboardView(ProfileTestMixin, TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(
            response, f"{self.login_url}?next={self.dashboard_url}"
        )
        self.login()
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/dashboard.html")


class TestProfileView(ProfileTestMixin, TestCase):
    def test_profile_view(self):
        self.login()
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/profile.html")
        self.assertContains(response, self.username)


class TestUpdateProfileView(ProfileTestMixin, TestCase):
    def test_get_update_profile(self):
        self.login()
        response = self.client.get(self.update_profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/update_profile.html")

    def test_post_update_profile_valid(self):
        self.login()
        response = self.client.post(
            self.update_profile_url,
            {"first_name": "New", "last_name": "Name"},
            follow=True,
        )
        self.assertRedirects(response, self.profile_url)
        self.assertContains(response, "Profile updated successfully.")
        user = User.objects.get(username=self.username)
        self.assertEqual(user.first_name, "New")
        self.assertEqual(user.last_name, "Name")


class TestResetPasswordView(ProfileTestMixin, TestCase):
    def test_get_reset_password(self):
        response = self.client.get(self.reset_password_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/password_reset.html")

    def test_post_invalid_form(self):
        response = self.client.post(self.reset_password_url, {}, follow=True)
        self.assertContains(response, "Invalid form submission.")
        self.assertTemplateUsed(response, "login/password_reset.html")

    def test_post_user_not_found(self):
        response = self.client.post(
            self.reset_password_url, {"username": "nouser"}, follow=True
        )
        self.assertContains(response, "User not found.")
        self.assertTemplateUsed(response, "login/password_reset.html")

    def test_post_success(self):
        with (
            patch(
                "login.utils.email_utils.send_email_to_user", return_value=True
            ),
            patch(
                "login.views.profile_views.generate_otp", return_value="654321"
            ),
        ):
            response = self.client.post(
                self.reset_password_url,
                {"username": self.username},
                follow=True,
            )
            self.assertContains(response, f"OTP sent to {self.email}.")
            self.assertTemplateUsed(response, "login/password_reset.html")
            session = self.client.session
            self.assertEqual(session["otp"], "654321")
            self.assertEqual(session["user"], self.username)
            self.assertTrue(session["email_otp_sent"])

    def test_get_with_email_otp_sent(self):
        session = self.client.session
        session["email_otp_sent"] = True
        session.save()
        response = self.client.get(self.reset_password_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/password_reset.html")


class TestVerifyOtpView(ProfileTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.session = self.client.session
        self.session["otp"] = "654321"
        self.session["user"] = self.username
        self.session.save()

    def test_invalid_method(self):
        response = self.client.get(self.verify_otp_url)
        self.assertRedirects(response, self.reset_password_url)

    def test_invalid_otp(self):
        response = self.client.post(
            self.verify_otp_url,
            {"otp": "wrong", "new_password": "x", "confirm_password": "x"},
            follow=True,
        )
        self.assertContains(response, "Invalid OTP.")
        self.assertTemplateUsed(response, "login/password_reset.html")

    def test_password_mismatch(self):
        response = self.client.post(
            self.verify_otp_url,
            {"otp": "654321", "new_password": "a", "confirm_password": "b"},
            follow=True,
        )
        self.assertContains(response, "Passwords do not match.")
        self.assertTemplateUsed(response, "login/password_reset.html")

    def test_success(self):
        response = self.client.post(
            self.verify_otp_url,
            {
                "otp": "654321",
                "new_password": "newpass",
                "confirm_password": "newpass",
            },
            follow=True,
        )
        self.assertContains(response, "Password reset successful")
        self.assertRedirects(response, self.login_url)
        user = User.objects.get(username=self.username)
        self.assertTrue(user.check_password("newpass"))
