from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import base64



class User(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    last_login = models.DateTimeField(null=True, blank=True)
    password = models.CharField(max_length=128)
    is_admin = models.BooleanField(default=False)
    account = models.ForeignKey('Account', on_delete=models.CASCADE, related_name='staff', null=True)
    confirmation_token = models.CharField(max_length=48)
    token = models.CharField(max_length=128)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email.__str__()

    @property
    def is_anonymous(self):
        """
        Always return False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True




class Account(models.Model):
    address = models.CharField(max_length=255, null=False, blank=False)
    is_admin = models.BooleanField(default=False)
    slug = models.SlugField()
    name = models.CharField(max_length=255, null=False, blank=False)

    def add_user(self, email):
        user = User.objects.filter(email=email).first()
        if user is None:
            AccountEmailCash.objects.create(account=self, email=email)
            return True
        elif user.account is None:
            user.account = self
            return True
        return False






class AccountEmailCash(models.Model):
    account = models.ForeignKey('Account', models.CASCADE, related_name='email_cash')
    email = models.EmailField(max_length=255, unique=True)

    class Meta:
        unique_together = ['account', 'email']
