from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from products.models import Product, Invoice, TARGETS, InvoiceChanges
from users.models import Address
from users.serializers import AccountSerializer
from ara.error_types import ADDRESS_INCONSISTENCY, INCORRECT_TARGET


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        exclude = ('responsible', )


class ResponsibleFilter(serializers.Serializer):
    show_own = serializers.NullBooleanField(default=None, required=False)


class TypeProductFilter(serializers.Serializer):
    type_filter = serializers.CharField(max_length=50, default='')


class AddressSerializer(serializers.Serializer):
    contact_name = serializers.CharField(max_length=255)
    contact_phone = PhoneNumberField()
    city = serializers.CharField(max_length=255)
    street = serializers.CharField(max_length=255)
    house = serializers.CharField(max_length=255)
    zip = serializers.CharField(max_length=255)


class CreateInvoiceSerializer(serializers.Serializer):
    products = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all())
    invoice_type = serializers.IntegerField()
    custom_address = AddressSerializer(required=False)
    address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), allow_null=True, allow_empty=True,
                                                 required=False)
    comment = serializers.CharField(allow_blank=True, default='')
    target = serializers.IntegerField()

    def validate(self, attrs):
        if 'address' in attrs and 'custom_address' in attrs:
            raise ValidationError(ADDRESS_INCONSISTENCY)
        elif 'address' not in attrs and 'custom_address' not in attrs:
            raise ValidationError(ADDRESS_INCONSISTENCY)
        elif not attrs['target'] in [0, 1, 2, 3]:
            raise ValidationError(INCORRECT_TARGET)
        else:
            return attrs

    def get_address(self):
        if 'address' in self.validated_data:
            return self.validated_data['address']
        elif 'custom_address' in self.validated_data:
            return Address.objects.create(**self.validated_data['custom_address'])
        return None


class CheckInvoiceSerializer(serializers.Serializer):
    products = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all())
    invoice_type = serializers.IntegerField()


class InvoiceChangesSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvoiceChanges
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):

    from_account = AccountSerializer()
    to_account = AccountSerializer()
    invoice_lines = ProductSerializer(many=True)
    address = AddressSerializer()
    invoice_changes = InvoiceChangesSerializer(many=True)


    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ('from_account', 'to_account', 'invoice_lines', 'address')

