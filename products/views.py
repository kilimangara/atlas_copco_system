from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from ara.response import SuccessResponse, ErrorResponse
from authentication.authentication import BasicAuthentication
from products.models import Product
from .serializers import ProductSerializer, ResponsibleFilter
from ara.error_types import NO_SUCH_PRODUCT
from rest_framework.pagination import PageNumberPagination

from users.serializers import AddressSerializer


@api_view(['GET', 'PUT'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def show_products(request):
    if request.method == 'GET':
        current_account = request.user.account
        responsible_filter_serializer = ResponsibleFilter(data=request.query_params)
        responsible_filter_serializer.is_valid(raise_exception=True)
        show_own_products = responsible_filter_serializer.validated_data['show_own']
        paginator = PageNumberPagination()
        products_query = []
        if show_own_products is None:
            products_query = Product.objects.all()
        elif show_own_products is False:
            products_query = Product.objects.exclude(responsible=current_account)
        elif show_own_products is True:
            products_query = Product.objects.filter(responsible=current_account)
        page = paginator.paginate_queryset(products_query, request)
        data = ProductSerializer(page, many=True).data
        return SuccessResponse(paginator.get_paginated_response(data).data, status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def show_product(request, product_id):
    if request.method == 'GET':
        try:
            product = Product.objects.get(pk=product_id)
        except ObjectDoesNotExist:
            return ErrorResponse(NO_SUCH_PRODUCT, status.HTTP_404_NOT_FOUND)
        return SuccessResponse(ProductSerializer(product).data, status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def create_invoice(request):
    user = request.user
