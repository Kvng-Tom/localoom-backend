from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomAuthBackend(ModelBackend):
    """
    Allow:
    - Buyers: email only
    - Artisans: email OR phone_number
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            
            if "@" in username:
                user = User.objects.get(email__iexact=username)
            else:
                user = User.objects.get(phone_number=username)
        except User.DoesNotExist:
            return None

        
        if user.role == User.Roles.BUYER and "@" not in username:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
