from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.contrib.auth import get_user_model
from allauth.account.utils import send_email_confirmation


class LiveAccountAdapter(DefaultAccountAdapter):
    def new_user(self, request):
        user_type = request.POST["user_type"]
        user_type = [user_type] if isinstance(user_type, str) else user_type
        assert isinstance(user_type, list)
        if any(group in settings.LIVE_ADMIN_USER_APPROVAL for group in user_type):
            # admin has to go through and manually
            # set users' active status to True
            user = get_user_model()(is_active=False)

            # we don't need to send the email within the else clause because
            # allauth will automatically do that (since user.is_active is True)
            send_email_confirmation(request, user, signup=True)
            # TODO: use allauth user_signed_up signal to send email?

            return user
        else:
            return super().new_user(request)
