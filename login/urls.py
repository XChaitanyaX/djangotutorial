from django.urls import path

from .views import auth_views, profile_views, quiz_views, file_views

app_name = "login"

urlpatterns = [
    path("", auth_views.LoginView.as_view(), name="login"),
    path("register/", auth_views.RegisterView.as_view(), name="register"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", profile_views.dashboard, name="dashboard"),
    path("profile/", profile_views.profile, name="profile"),
    path(
        "reset_password/", profile_views.reset_password, name="reset_password"
    ),
    path(
        "update_profile/",
        profile_views.UpdateProfileView.as_view(),
        name="update_profile",
    ),
    path("verify_otp/", profile_views.verify_otp, name="verify_otp"),
    path("questions/", quiz_views.Questions.as_view(), name="questions"),
    path("result/", quiz_views.result, name="result"),
    path("file_upload/", file_views.file_upload, name="file_upload"),
]
