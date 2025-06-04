from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

from ..forms import PasswordResetForm, ProfileUpdateForm, UsernameForm
from ..utils.email_utils import generate_otp, send_email_to_user


@login_required(login_url="login:login")
@never_cache
def dashboard(request):
    return render(request, "login/dashboard.html")


@login_required(login_url="login:login")
@never_cache
def profile(request):
    user = request.user
    return render(request, "login/profile.html", {"user": user})


@method_decorator(
    [login_required(login_url="login:login"), never_cache],
    name="dispatch",
)
class UpdateProfileView(View):
    def get(self, request):
        form = ProfileUpdateForm()
        return render(request, "login/update_profile.html", {"form": form})

    def post(self, request):
        form = ProfileUpdateForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            user = request.user

            user.first_name = first_name
            user.last_name = last_name
            user.save()

            messages.success(request, "Profile updated successfully.")
            return redirect(reverse("login:profile"))
        else:
            form = ProfileUpdateForm()
            messages.error(request, "Error updating profile.")
        return render(request, "login/update_profile.html", {"form": form})


@never_cache
def reset_password(request):
    if request.method == "POST":
        form = UsernameForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            user = User.objects.filter(username=username).first()
            if not user:
                messages.error(request, "User not found.")
                return redirect(reverse("login:reset_password"))
            request.session["user"] = user.username
            user_email = user.email
            print(f"User email: {user_email}")

            otp = generate_otp()
            status = send_email_to_user(
                "Password Reset OTP",
                f"Your OTP for password reset is: {otp}",
                [user_email],
            )
            if status:
                request.session["otp"] = otp
                request.session["email_otp_sent"] = True
                messages.success(request, f"OTP sent to {user_email}.")
                return redirect(reverse("login:reset_password"))
            else:
                messages.error(request, "Failed to send email.")
        else:
            messages.error(request, "Invalid form submission.")
    else:
        if request.session.get("email_otp_sent", None):
            form = PasswordResetForm()
        else:
            form = UsernameForm()
    return render(request, "login/password_reset.html", {"form": form})


@never_cache
def verify_otp(request):
    if request.method != "POST":
        return redirect("login:reset_password")

    otp = request.POST.get("otp")
    if otp != request.session.get("otp"):
        messages.error(request, "Invalid OTP.")
        return redirect("login:reset_password")

    user = get_object_or_404(User, username=request.session.get("user"))

    new_password = request.POST.get("new_password")
    confirm_password = request.POST.get("confirm_password")
    if new_password == confirm_password:
        user.set_password(new_password)
        user.save()

        messages.success(
            request, "Password reset successful. You can now log in."
        )
        request.session.flush()
        return redirect(reverse("login:login"))
    else:
        messages.error(request, "Passwords do not match.")
        return redirect("login:reset_password")
