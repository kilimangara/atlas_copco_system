from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from ara.response import SuccessResponse, ErrorResponse
from authentication.authentication import BasicAuthentication
from products.models import Product
from .serializers import ProductSerializer
from ara.error_types import NO_SUCH_PRODUCT


@api_view(['GET', 'PUT'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def products(request):
    if request.method == 'GET':
        return SuccessResponse(ProductSerializer(Product.objects.all(), many=True).data, status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def product(request, product_id):
    if request.method == 'GET':
        try:
            product = Product.objects.get(pk=product_id)
        except ObjectDoesNotExist:
            return ErrorResponse(NO_SUCH_PRODUCT, status.HTTP_404_NOT_FOUND)
        return SuccessResponse(ProductSerializer(product).data, status.HTTP_200_OK)

