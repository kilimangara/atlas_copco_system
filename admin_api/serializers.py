from users.models import User, Account
from products.models import Product
from rest_framework.serializers import Serializer, ModelSerializer


class ProductSerializer(ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'



class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'



class AccountSerializer(ModelSerializer):

    class Meta:
        model = Account
        fields = '__all__'