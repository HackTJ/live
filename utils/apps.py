from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = "utils"

    def ready(self):
        from allauth.account.signals import user_signed_up
        from .signals import confirm_email_immediately

        user_signed_up.connect(confirm_email_immediately, dispatch_uid="user_signed_up")
