import secrets
import string
import time
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.validators import validate_email

OTP_EXPIRE_TIME = 300


def generate_otp(length=6):
    return "".join(secrets.choice(string.digits) for _ in range(length))


def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def send_verification_otp_email(email, request):
    otp = generate_otp()
    subject = "OTP for Verification"
    message = f"Your OTP is: {otp}"
    from_email = settings.EMAIL_HOST_USER
    if send_mail(subject, message, from_email, [email]):
        request.session["otp"] = otp
        request.session["otp_sent_time"] = time.time()
        request.session["email_otp_sent"] = True
        return True
    return False


def is_valid_otp(request, otp):
    if "otp" in request.session and "otp_sent_time" in request.session:
        sent_otp = request.session["otp"]
        sent_time = request.session["otp_sent_time"]
        current_time = time.time()
        if current_time - sent_time <= OTP_EXPIRE_TIME:
            return sent_otp == otp
    return False


def send_email_to_user(subject, message, user_emails):
    from_email = settings.EMAIL_HOST_USER
    status = send_mail(
        subject, message, from_email, user_emails, fail_silently=False
    )
    return status == len(user_emails)
