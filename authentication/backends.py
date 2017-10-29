from django.core.exceptions import ObjectDoesNotExist

from users.models import User


class TokenAuthenticationBackend(object):

    def authenticate(self, token):
        return User.objects.filter(token=token).first()

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return None