from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


<<<<<<< HEAD
class AuthViewTests(TestCase):
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

    def get_csrf(self, url):
        return self.client.get(url).cookies["csrftoken"].value

    def test_login_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/login.html")

    def test_login_valid(self):
        response = self.client.post(
            self.login_url,
            {
                "username": self.username,
                "password": self.password,
                "csrfmiddlewaretoken": self.get_csrf(self.login_url),
            },
=======

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
>>>>>>> 8b42987c325364c9574c556d8de3490eadb31b80
        )
        self.assertTrue(is_valid_cred)

<<<<<<< HEAD
    def test_login_invalid(self):
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

    def test_login_invalid_form(self):
        response = self.client.post(
            self.login_url,
            {"csrfmiddlewaretoken": self.get_csrf(self.login_url)},
            follow=True,
        )
        self.assertContains(response, "Invalid form submission.")
        self.assertTemplateUsed(response, "login/login.html")

    def test_logout(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)

    def test_register_get_email(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/register.html")
        self.assertIn("form", response.context)

    def test_register_post_invalid_email(self):
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

    def test_register_post_valid_email(self):
        from unittest.mock import patch

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
            self.assertTrue("email_otp_sent" in self.client.session)
            self.assertTrue("email" in self.client.session)

    def test_register_post_otp_invalid(self):
        session = self.client.session
        session["email_otp_sent"] = True
        session["otp"] = "123456"
        session["email"] = "new@user.com"
        session.save()
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

    def test_register_post_username_exists(self):
        session = self.client.session
        session["email_otp_sent"] = True
        session["otp"] = "123456"
        session["email"] = "new@user.com"
        session.save()
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

    def test_register_post_password_mismatch(self):
        session = self.client.session
        session["email_otp_sent"] = True
        session["otp"] = "123456"
        session["email"] = "new@user.com"
        session.save()
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

    def test_register_post_success(self):
        session = self.client.session
        session["email_otp_sent"] = True
        session["otp"] = "123456"
        session["email"] = "new@user.com"
        session.save()
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


class ProfileViewTests(TestCase):
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
        self.update_user_profile_url = reverse("login:update_user_profile")
        self.update_profile_url = reverse("login:update_profile")
        self.reset_password_url = reverse("login:reset_password")
        self.verify_otp_url = reverse("login:verify_otp")

    def login(self):
        self.client.login(username=self.username, password=self.password)

    def test_dashboard_requires_login(self):
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(
            response, f"{self.login_url}?next={self.dashboard_url}"
        )
        self.login()
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/dashboard.html")

    def test_profile_view(self):
        self.login()
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/profile.html")
        self.assertContains(response, self.username)

    def test_update_user_profile_get(self):
        self.login()
        response = self.client.get(self.update_user_profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/update_profile.html")

    def test_update_profile_post(self):
        self.login()
        response = self.client.post(
            self.update_profile_url,
            {"first_name": "New", "last_name": "Name"},
            follow=True,
        )
        self.assertRedirects(response, self.dashboard_url)
        self.assertContains(response, "Profile updated successfully.")
        user = User.objects.get(username=self.username)
        self.assertEqual(user.first_name, "New")
        self.assertEqual(user.last_name, "Name")

    def test_update_profile_invalid_method(self):
        self.login()
        response = self.client.get(self.update_profile_url, follow=True)
        self.assertContains(response, "Invalid request method.")
        self.assertRedirects(response, self.dashboard_url)

    def test_reset_password_get(self):
        response = self.client.get(self.reset_password_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/password_reset.html")

    def test_reset_password_post_invalid_form(self):
        response = self.client.post(self.reset_password_url, {}, follow=True)
        self.assertContains(response, "Invalid form submission.")
        self.assertTemplateUsed(response, "login/password_reset.html")

    def test_reset_password_post_user_not_found(self):
        response = self.client.post(
            self.reset_password_url, {"username": "nouser"}, follow=True
        )
        self.assertContains(response, "User not found.")
        self.assertTemplateUsed(response, "login/password_reset.html")

    def test_reset_password_post_success(self):
        from unittest.mock import patch

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

    def test_reset_password_post_email_otp_sent(self):
        session = self.client.session
        session["email_otp_sent"] = True
        session.save()
        response = self.client.get(self.reset_password_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login/password_reset.html")

    def test_verify_otp_invalid_method(self):
        response = self.client.get(self.verify_otp_url)
        self.assertRedirects(response, self.reset_password_url)

    def test_verify_otp_invalid_otp(self):
        session = self.client.session
        session["otp"] = "654321"
        session["user"] = self.username
        session.save()
        response = self.client.post(
            self.verify_otp_url,
            {"otp": "wrong", "new_password": "x", "confirm_password": "x"},
            follow=True,
        )
        self.assertContains(response, "Invalid OTP.")
        self.assertTemplateUsed(response, "login/password_reset.html")

    def test_verify_otp_password_mismatch(self):
        session = self.client.session
        session["otp"] = "654321"
        session["user"] = self.username
        session.save()
        response = self.client.post(
            self.verify_otp_url,
            {"otp": "654321", "new_password": "a", "confirm_password": "b"},
            follow=True,
        )
        self.assertContains(response, "Passwords do not match.")
        self.assertTemplateUsed(response, "login/password_reset.html")

    def test_verify_otp_success(self):
        session = self.client.session
        session["otp"] = "654321"
        session["user"] = self.username
        session.save()
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
=======
    def test_invalid_credentials(self):
        is_valid_cred = self.client.login(username="user", password="password")
        self.assertFalse(is_valid_cred)
>>>>>>> 8b42987c325364c9574c556d8de3490eadb31b80
