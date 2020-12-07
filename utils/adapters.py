from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.contrib.auth import get_user_model


class LiveAccountAdapter(DefaultAccountAdapter):
    def new_user(self, request):
        if settings.LIVE_ADMIN_VERIFICATION:
            # admin has to go through and manually
            # set users' active status to True
            user = get_user_model()(is_active=False)
            return user
        else:
            return super().new_user(request)
