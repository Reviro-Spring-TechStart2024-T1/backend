from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created

from .models import User


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    base_url = instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm'))

    # Modify the URL prefix
    if base_url.startswith('https'):
        custom_url = base_url.replace('https', 'drink', 1)
    elif base_url.startswith('http'):
        custom_url = base_url.replace('http', 'drink', 1)
    else:
        custom_url = base_url

    frontend_url = 'https://reviro-frontend.vercel.app/forgot-password'

    context = {
        'current_user': reset_password_token.user,
        'email': reset_password_token.user.email,
        'reset_password_url_1': f'{base_url}?token={reset_password_token.key}',
        'reset_password_url_2': f'{custom_url}?token={reset_password_token.key}',
        'reset_password_url_3': f'{frontend_url}?token={reset_password_token.key}'
    }

    # render email text
    email_html_message = render_to_string('email/user_reset_password.html', context)
    email_plaintext_message = render_to_string('email/user_reset_password.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        'Password Reset for {title}'.format(title='Some website title'),
        # message:
        email_plaintext_message,
        # from:
        'noreply@somehost.local',
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, 'text/html')
    msg.send()


@receiver(post_save, sender=User)
def block_partner(sender, instance, **kwargs):
    if instance.is_blocked:
        instance.soft_delete_related_objects()
    else:
        instance.restore_related_objects()
