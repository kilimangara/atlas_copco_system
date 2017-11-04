from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from products.models import Product, Invoice
from users.models import Address
from users.serializers import AccountSerializer, AddressSerializer
from ara.error_types import ADDRESS_INCONSISTENCY


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        exclude = ('responsible', )


class ResponsibleFilter(serializers.Serializer):
    show_own = serializers.NullBooleanField(default=None, required=False)



class CreateInvoiceSerializer(serializers.Serializer):
    products = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all())
    invoice_type = serializers.IntegerField()
    address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), allow_null=True, allow_empty=True)
    custom_address = AddressSerializer(allow_null=True),
    comment = serializers.CharField(allow_blank=True, default='')

    def validate(self, attrs):
        if 'address' in attrs and 'custom_address' in attrs:
            raise ValidationError(ADDRESS_INCONSISTENCY)
        elif 'address' not in attrs and 'custom_address' not in attrs:
            raise ValidationError(ADDRESS_INCONSISTENCY)
        else:
            return attrs


class InvoiceSerializer(serializers.ModelSerializer):

    from_account = AccountSerializer()
    to_account = AccountSerializer()
    invoice_lines = ProductSerializer(many=True)
    address = AddressSerializer()


    class Meta:
        model = Invoice
        exclude = ('on_creation',)
        read_only_fields = ('from_account', 'to_account', 'invoice_lines', 'address')

