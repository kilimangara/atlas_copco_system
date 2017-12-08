from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from phonenumber_field.modelfields import PhoneNumberField


class User(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    last_login = models.DateTimeField(null=True, blank=True)
    password = models.CharField(max_length=128)
    is_admin = models.BooleanField(default=False)
    account = models.ForeignKey('Account', on_delete=models.CASCADE, related_name='staff', null=True, blank=True)
    confirmation_token = models.CharField(max_length=48, blank=True)
    token = models.CharField(max_length=128)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.name +' '+self.email.__str__()

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
    address = models.OneToOneField('Address', models.CASCADE, related_name='account', null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    slug = models.SlugField(unique=True)
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

    def get_admin_name(self):
        admin = self.staff.filter(is_admin=True).first()
        if admin:
            return admin.name
        return self.name

    def __str__(self):
        return self.name


class Address(models.Model):
    contact_name = models.CharField(max_length=255, blank=True)
    contact_phone = PhoneNumberField(blank=True)
    city = models.CharField(max_length=255, blank=True)
    street = models.CharField(max_length=255, blank=True)
    zip = models.CharField(max_length=20, blank=True)
    house = models.CharField(max_length=7, blank=True)

    def __str__(self):
        return '{} {} {}'.format(self.street, self.house, self.contact_name)


class AccountEmailCash(models.Model):
    account = models.ForeignKey('Account', models.CASCADE, related_name='email_cash')
    email = models.EmailField(max_length=255, unique=True)

    class Meta:
        unique_together = ['account', 'email']
