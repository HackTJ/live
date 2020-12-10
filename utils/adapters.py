from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.contrib.auth import get_user_model


class LiveAccountAdapter(DefaultAccountAdapter):
    def new_user(self, request):
        user_type = request.POST["user_type"]
        user_type = [user_type] if isinstance(user_type, str) else user_type
        assert isinstance(user_type, list)
        if any(group in settings.LIVE_ADMIN_USER_APPROVAL for group in user_type):
            # admin has to go through and manually
            # set users' active status to True
            user = get_user_model()(is_active=False)

            return user
        else:
            return super().new_user(request)
