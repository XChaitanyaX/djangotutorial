from django import forms


class UsernameForm(forms.Form):
    username = forms.CharField(
        label="Username",
        max_length=150,
    )


class EmailForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254, required=True)


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        max_length=150,
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
    )


class RegistrationForm(forms.Form):
    username = forms.CharField(
        label="Username",
        max_length=150,
    )
    otp = forms.CharField(
        label="OTP",
        max_length=6,
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
    )


class PasswordResetForm(forms.Form):
    password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput,
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
    )
    otp = forms.CharField(
        label="OTP",
        max_length=6,
    )


class FileUploadForm(forms.Form):
    file = forms.FileField()


class ProfileUpdateForm(forms.Form):
    first_name = forms.CharField(
        label="First Name",
        max_length=30,
        required=False,
    )
    last_name = forms.CharField(
        label="Last Name",
        max_length=30,
        required=False,
    )
