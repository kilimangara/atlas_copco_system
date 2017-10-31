from rest_framework import serializers

from products.models import Product
from users.serializers import AccountSerializer


class ProductSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        admin = instance.responsible.get_admin()
        data = super().to_representation(instance)
        data.update({'responsible': admin.name})
        return data

    class Meta:
        model = Product
        fields = '__all__'
