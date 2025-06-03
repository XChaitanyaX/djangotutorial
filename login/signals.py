from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import Question
from mysite.settings import EMAIL_HOST_USER


@receiver(post_save, sender=Question)
def send_mail_on_new_question(sender, instance, created, **kwargs):
    if created:
        receiptent_list = [
            user.email for user in User.objects.all() if user.email
        ]

        if not receiptent_list:
            return

        send_mail(
            subject="New Question Created",
            message="""
                Welcome Candidate
                A new question has been added.
                Please login to answer it.
            """,
            from_email=EMAIL_HOST_USER,
            recipient_list=receiptent_list,
            fail_silently=False,
        )


@receiver(post_save, sender=User)
def send_mail_on_new_user(sender, instance, created, **kwargs):
    if created and instance.email:
        send_mail(
            subject="Welcome to the Quiz App",
            message="""
                Welcome Candidate,
                You have successfully registered.
                Please login to answer the questions.
            """,
            from_email=EMAIL_HOST_USER,
            recipient_list=[instance.email],
            fail_silently=False,
        )
