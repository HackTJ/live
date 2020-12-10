from allauth.account.utils import send_email_confirmation


def confirm_email_immediately(request, user):
    # TODO: functools partial?
    send_email_confirmation(request, user, signup=True, email=user.email)
