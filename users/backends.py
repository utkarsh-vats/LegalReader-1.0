from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        login_identifiers = username or kwargs.get('login_id')
        if not login_identifiers or password is None:
            return None
        try:
            user = User.objects.get(Q(email__iexact=login_identifiers) | Q(phone_number__iexact=login_identifiers))
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None



