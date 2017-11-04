from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from ara.response import SuccessResponse, ErrorResponse
from authentication.authentication import BasicAuthentication
from products.models import Product, TYPES, Invoice
from .serializers import ProductSerializer, ResponsibleFilter, CreateInvoiceSerializer, InvoiceSerializer
from ara.error_types import NO_SUCH_PRODUCT, INCORRECT_INVOICE_TYPE, INCORRECT_INVOICE_PRODUCTS
from rest_framework.pagination import PageNumberPagination

from users.serializers import AddressSerializer


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_filters(request):
    arr = Product.objects.only('type_filter').distinct('type_filter')
    filtered_arr = map(lambda prod: prod.type_filter, arr)
    return SuccessResponse(filtered_arr,status.HTTP_200_OK)


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
def check_invoice(request):
    user = request.user
    invoice_serializer = CreateInvoiceSerializer(data=request.data)
    invoice_serializer.is_valid(raise_exception=True)
    if not invoice_serializer.validated_data['invoice_type'] in TYPES:
        ErrorResponse(INCORRECT_INVOICE_TYPE, status.HTTP_400_BAD_REQUEST)
    filtered_products = list(filter(lambda prod: not prod.responsible == user.account, invoice_serializer.validated_data['products']))
    if len(filtered_products) == len(invoice_serializer.validated_data['products']):
        print(list(set(map(lambda pr: pr.responsible, invoice_serializer.validated_data['products']))))
        # invoice = Invoice.objects.create()
        return SuccessResponse({'status': 'ok', 'invoice_type': 0}, status.HTTP_200_OK)
    elif len(filtered_products) == 0:
        return SuccessResponse({'status': 'ok', 'invoice_type': 1}, status.HTTP_200_OK)
    else:
        return ErrorResponse(INCORRECT_INVOICE_PRODUCTS, status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def create_invoice(request):
    user = request.user
    invoice_serializer = CreateInvoiceSerializer(data=request.data)
    invoice_serializer.is_valid(raise_exception=True)
    print(invoice_serializer.validated_data['products'])
    return SuccessResponse({'status':'ok'})
