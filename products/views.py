from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from ara.response import SuccessResponse, ErrorResponse
from authentication.authentication import BasicAuthentication
from products.models import Product, TYPES, Invoice, InvoiceChanges, STATUSES
from .serializers import ProductSerializer, ResponsibleFilter, CreateInvoiceSerializer, InvoiceSerializer, \
    CheckInvoiceSerializer, TypeProductFilter
from ara.error_types import NO_SUCH_PRODUCT, INCORRECT_INVOICE_TYPE, INCORRECT_INVOICE_PRODUCTS
from .pagination import CountHeaderPagination


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_filters(request):
    arr = Product.objects.only('type_filter').distinct('type_filter')
    filtered_arr = map(lambda prod: prod.type_filter, arr)
    return SuccessResponse(filtered_arr, status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def show_products(request):
    if request.method == 'GET':
        current_account = request.user.account
        responsible_filter_serializer = ResponsibleFilter(data=request.query_params)
        responsible_filter_serializer.is_valid(raise_exception=True)
        type_filter_serializer = TypeProductFilter(data=request.query_params)
        type_filter_serializer.is_valid(raise_exception=True)
        type_filter = type_filter_serializer.validated_data['type_filter']
        show_own_products = responsible_filter_serializer.validated_data['show_own']
        paginator = CountHeaderPagination()
        paginator.page_size_query_param = 'page_size'
        products_query = []
        if show_own_products is None:
            products_query = Product.objects.filter(type_filter=type_filter) if type_filter != '' else Product.objects.all()
        elif show_own_products is False:
            products_query = Product.objects.exclude(responsible=current_account).filter(type_filter=type_filter) \
            if type_filter != '' else Product.objects.exclude(responsible=current_account)
        elif show_own_products is True:
            products_query = Product.objects.filter(responsible=current_account, type_filter=type_filter) \
            if type_filter != '' else Product.objects.filter(responsible=current_account)
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
    invoice_serializer = CheckInvoiceSerializer(data=request.data)
    invoice_serializer.is_valid(raise_exception=True)
    if not invoice_serializer.validated_data['invoice_type'] in TYPES:
        ErrorResponse(INCORRECT_INVOICE_TYPE, status.HTTP_400_BAD_REQUEST)
    filtered_products = list(
        filter(lambda prod: not prod.responsible == user.account, invoice_serializer.validated_data['products']))
    invoice_type = invoice_serializer.validated_data['invoice_type']
    if len(filtered_products) == len(invoice_serializer.validated_data['products']):
        account_ids = list(set(map(lambda prod: prod.responsible.id, invoice_serializer.validated_data['products'])))
        if invoice_type == 0:
            return SuccessResponse({'status': 'ok', 'invoice_type': 0, 'accounts': account_ids}, status.HTTP_200_OK)
        else:
            return ErrorResponse(INCORRECT_INVOICE_TYPE, status.HTTP_400_BAD_REQUEST)
    elif len(filtered_products) == 0:
        if invoice_type in [1, 2]:
            return SuccessResponse(
                {'status': 'ok', 'invoice_type': invoice_type, "accounts": [request.user.account.id]},
                status.HTTP_200_OK)
        else:
            return ErrorResponse(INCORRECT_INVOICE_TYPE, status.HTTP_400_BAD_REQUEST)
    else:
        return ErrorResponse(INCORRECT_INVOICE_PRODUCTS, status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def create_invoice(request):
    user = request.user
    current_account = user.account
    invoice_serializer = CreateInvoiceSerializer(data=request.data)
    invoice_serializer.is_valid(raise_exception=True)
    if not invoice_serializer.validated_data['invoice_type'] in TYPES:
        ErrorResponse(INCORRECT_INVOICE_TYPE, status.HTTP_400_BAD_REQUEST)
    address = invoice_serializer.get_address()
    print(address.id)
    invoice_type = invoice_serializer.validated_data['invoice_type']
    products = invoice_serializer.validated_data['products']
    comment = invoice_serializer.validated_data['comment']
    target = invoice_serializer.validated_data['target']
    filtered_products = list(
        filter(lambda prod: not prod.responsible == user.account, products))
    if len(filtered_products) == len(products):
        if invoice_type == 0:
            accounts = list(set(map(lambda pr: pr.responsible, products)))
            created_invoices = []
            for account in accounts:
                account_products = list(filter(lambda pr: pr.responsible.id == account.id, products))
                invoice = Invoice.objects.create(invoice_type=invoice_type, comment=comment,
                                                 address=address, from_account=current_account, to_account=account,
                                                 target=target)
                invoice.invoice_lines.add(*account_products)
                invoice.save()
                InvoiceChanges.objects.create(invoice=invoice, status=0)
                created_invoices.append(invoice)
            return SuccessResponse(InvoiceSerializer(created_invoices, many=True).data, status.HTTP_200_OK)
        else:
            return ErrorResponse(INCORRECT_INVOICE_TYPE, status.HTTP_400_BAD_REQUEST)
    elif len(filtered_products) == 0:
        if invoice_type == 0:
            invoice = Invoice.objects.create(invoice_type=invoice_type, comment=comment,
                                             address=address, from_account=current_account, to_account=current_account,
                                             target=target)
            invoice.invoice_lines.add(*products)
            invoice.save()
            InvoiceChanges.objects.create(invoice=invoice, status=0)
            return SuccessResponse(InvoiceSerializer(invoice).data, status.HTTP_200_OK)
        else:
            return ErrorResponse(INCORRECT_INVOICE_TYPE, status.HTTP_400_BAD_REQUEST)
    else:
        return ErrorResponse(INCORRECT_INVOICE_PRODUCTS, status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_invoices(request):
    user = request.user
    current_account = user.account
    paginator = CountHeaderPagination()
    paginator.page_size_query_param = 'page_size'
    if current_account.is_admin:
        invoices = Invoice.objects.all()
    else:
        invoices = Invoice.objects.filter(to_account=current_account)
    page = paginator.paginate_queryset(invoices, request)
    data = InvoiceSerializer(page, many=True).data
    return SuccessResponse(paginator.get_paginated_response(data).data, status.HTTP_200_OK)
