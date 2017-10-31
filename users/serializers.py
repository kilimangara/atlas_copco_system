from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from ara.error_types import PASSWORD_INCORRECT
from users.models import User, Account, Address


class ErrorToString(object):
    @property
    def errors_to_text(self):
        assert isinstance(self, serializers.Serializer)
        errors_list = []
        for field, field_errors in self.errors.items():
            if not field_errors:
                continue
            errors_list.append('{}: {}'.format(field, field_errors[0]))
        text = ' '.join(errors_list)
        return text


class CreateUserSerializer(serializers.Serializer, ErrorToString):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=50)
    password_confirmation = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=255)

    def validate(self, attrs):
        print(attrs)
        if not attrs['password'] == attrs['password_confirmation']:
            raise ValidationError(PASSWORD_INCORRECT)
        return attrs


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        exclude = ('account',)

class AccountSerializer(serializers.ModelSerializer):

    account = AddressSerializer()

    class Meta:
        model = Account
        fields = '__all__'




class ImportUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class UserSerializer(serializers.ModelSerializer):

    account = AccountSerializer()

    class Meta:
        model = User
        exclude = ('token', 'confirmation_token', 'password')
