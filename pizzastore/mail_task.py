from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def payment_mail(subject,message,tosend,html_message):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [tosend],
        html_message=html_message
    )
    return None