from rest_framework import serializers

from products.models import Product


class ProductSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update({'responsible': instance.responsible.name})
        return data

    class Meta:
        model = Product
        fields = '__all__'


class ResponsibleFilter(serializers.Serializer):
    show_own = serializers.NullBooleanField(default=None, required=False)



class CreateInvoiceSerializer(serializers.Serializer):
    products = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all())
