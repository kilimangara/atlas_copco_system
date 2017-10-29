from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


from users.models import User


class BasicAuthentication(TokenAuthentication):

    def authenticate_credentials(self, key):
        try:
            user = User.objects.get(token=key)
            # user.last_login = timezone.now()
            # user.save()
        except ObjectDoesNotExist:
            raise AuthenticationFailed()
        return user, key
