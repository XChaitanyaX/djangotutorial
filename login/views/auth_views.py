from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import (
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

from ..forms import EmailForm, LoginForm, RegistrationForm
from ..utils.email_utils import send_verification_otp_email


@method_decorator(never_cache, name="post")
class LoginView(View):
    def get(self, request) -> HttpResponse:
        request.session.flush()
        return render(request, "login/login.html", {"form": LoginForm()})

    def post(
        self, request
    ) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect(reverse("login:dashboard"))
            else:
                messages.error(request, "Invalid username or password.")
                return redirect("login:login")
        else:
            messages.error(request, "Invalid form submission.")
            return redirect("login:login")


@method_decorator(never_cache, name="post")
class RegisterView(View):
    def get(self, request) -> HttpResponse:
        if request.session.get("email_otp_sent", None):
            return render(
                request, "login/register.html", {"form": RegistrationForm()}
            )
        else:
            return render(
                request, "login/register.html", {"form": EmailForm()}
            )

    def post(
        self, request
    ) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
        if not request.session.get("email_otp_sent", None):
            email = request.POST.get("email")
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, "Invalid email address.")
                return redirect("login:register")

            if send_verification_otp_email(email, request):
                request.session["email"] = email
                messages.success(request, "OTP sent to your email.")
                return redirect(reverse("login:register"))

            messages.error(request, "Failed to send OTP.")
            return redirect("login:register")

        else:
            return user_registration(request)


class LogoutView(View):
    def get(
        self, request
    ) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
        logout(request)
        return redirect(reverse("login:login"))


@never_cache
def user_registration(
    request,
) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
    if request.method != "POST":
        return redirect("login:register")

    username = request.POST.get("username")
    email = request.session.get("email")
    otp = request.POST.get("otp")
    session_otp = request.session.get("otp")
    if not session_otp or otp != session_otp:
        messages.error(request, "Invalid OTP.")
        return redirect("login:register")

    password = request.POST.get("password")
    confirm_password = request.POST.get("confirm_password")
    if password == confirm_password:
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("login:register")
        user = User.objects.create_user(
            username=username, password=password, email=email
        )
        user.save()

        messages.success(
            request, "Registration successful. You can now log in."
        )
        return redirect(reverse("login:login"))

    else:
        messages.error(
            request, "Registration failed. Please check your details."
        )
        return redirect("login:register")
