from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone
from django_bulk_update.helper import bulk_update
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes, schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.schemas import AutoSchema

from ara.response import SuccessResponse, ErrorResponse
from authentication.authentication import BasicAuthentication
from products.models import Product, TYPES, Invoice, InvoiceChanges, STATUSES
from .serializers import ProductSerializer, ResponsibleFilter, CreateInvoiceSerializer, InvoiceSerializer, \
    CheckInvoiceSerializer, TypeProductFilter, InnerTypeProductFilter, StatusFilterSerializer
from ara.error_types import NO_SUCH_PRODUCT, INCORRECT_INVOICE_TYPE, INCORRECT_INVOICE_PRODUCTS, \
    SOME_PRODUCTS_ARE_IN_TRANSITION, INCORRECT_ID_PATTERN, INVOICE_UPDATE_ERROR
from .pagination import CountHeaderPagination


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_filters(request):
    """
     Получение всех доступных типов инструментов
    """
    arr = Product.objects.only('type_filter').distinct('type_filter')
    filtered_arr = map(lambda prod: prod.type_filter, arr)
    return SuccessResponse(filtered_arr, status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_inner_filters(request):
    """
     Получение всех доступных типов инструментов
    """
    serializer = TypeProductFilter(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    type_filter = serializer.validated_data['type_filter']
    arr = Product.objects.only('type_filter', 'inner_type_filter').filter(type_filter=type_filter).distinct('inner_type_filter')
    filtered_arr = map(lambda prod: prod.inner_type_filter, arr)
    return SuccessResponse(filtered_arr, status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def show_products(request):
    """
    Получение инструментов

    """
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


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def show_products_for_invoice(request):
    user = request.user
    current_account = user.account
    responsible_filter_serializer = ResponsibleFilter(data=request.query_params)
    responsible_filter_serializer.is_valid(raise_exception=True)
    show_own_products = responsible_filter_serializer.validated_data['show_own']
    paginator = CountHeaderPagination()
    paginator.page_size_query_param = 'page_size'
    products_query = []
    if show_own_products is None:
        products_query = Product.objects.filter(on_transition=False)
    elif show_own_products is False:
        products_query = Product.objects.exclude(responsible=current_account).filter(on_transition=False)
    elif show_own_products is True:
        products_query = Product.objects.filter(responsible=current_account, on_transition=False)
    page = paginator.paginate_queryset(products_query, request)
    data = ProductSerializer(page, many=True).data
    return SuccessResponse(paginator.get_paginated_response(data).data, status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
@schema(AutoSchema())
def show_product(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except ObjectDoesNotExist:
        return ErrorResponse(NO_SUCH_PRODUCT, status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return SuccessResponse(ProductSerializer(product).data, status.HTTP_200_OK)
    elif request.method == 'PUT':
        product_serializer = ProductSerializer(product, data=request.data, partial=True)
        product_serializer.is_valid(raise_exception=True)
        product_serializer.save()
        return SuccessResponse(product_serializer.data, status.HTTP_200_OK)


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
            return SuccessResponse({'status': 'ok', 'invoice_type': 0,
                                    'from_account': account_ids, 'to_account': request.user.account.id }, status.HTTP_200_OK)
        else:
            return ErrorResponse(INCORRECT_INVOICE_TYPE, status.HTTP_400_BAD_REQUEST)
    elif len(filtered_products) == 0:
        if invoice_type in [1, 2]:
            return SuccessResponse(
                {'status': 'ok', 'invoice_type': invoice_type,
                 "from_account": [request.user.account.id]},
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
    if not invoice_serializer.validated_data['invoice_type'] in [0, 1, 2]:
        return ErrorResponse(INCORRECT_INVOICE_TYPE, status.HTTP_400_BAD_REQUEST)
    address = invoice_serializer.get_address()
    invoice_type = invoice_serializer.validated_data['invoice_type']
    products = invoice_serializer.validated_data['products']
    comment = invoice_serializer.validated_data['comment']
    target = invoice_serializer.validated_data['target']
    if len(list(filter(lambda prod: prod.on_transition, products))) != 0:
        return ErrorResponse(SOME_PRODUCTS_ARE_IN_TRANSITION, status.HTTP_400_BAD_REQUEST)
    filtered_products = list(
        filter(lambda prod: not prod.responsible == user.account, products))
    if len(filtered_products) == len(products):
        if invoice_type == 0:
            accounts = list(set(map(lambda pr: pr.responsible, products)))
            created_invoices = []
            for account in accounts:
                account_products = list(filter(lambda pr: pr.responsible.id == account.id, products))
                invoice = Invoice.objects.create(invoice_type=invoice_type, comment=comment,
                                                 address=address, from_account=account, to_account=current_account,
                                                 target=target)
                invoice.invoice_lines.add(*account_products)
                invoice.save()
                InvoiceChanges.objects.create(invoice=invoice, status=0)
                created_invoices.append(invoice)
            return SuccessResponse(InvoiceSerializer(created_invoices, many=True).data, status.HTTP_200_OK)
        else:
            return ErrorResponse(INCORRECT_INVOICE_TYPE, status.HTTP_400_BAD_REQUEST)
    elif len(filtered_products) == 0:
        if invoice_type == 1:
            to_account = current_account if invoice_serializer.validated_data['to_account'] is None\
                else invoice_serializer.validated_data['to_account']
            invoice = Invoice.objects.create(invoice_type=invoice_type, comment=comment,
                                             address=address, from_account=current_account, to_account=to_account,
                                             target=target)
            invoice.invoice_lines.add(*products)
            invoice.save()
            InvoiceChanges.objects.create(invoice=invoice, status=0)
            return SuccessResponse(InvoiceSerializer(invoice).data, status.HTTP_200_OK)
        elif invoice_type == 2:
            to_account = current_account if invoice_serializer.validated_data['to_account'] is None \
                else invoice_serializer.validated_data['to_account']
            invoice = Invoice.objects.create(invoice_type=invoice_type, comment=comment,
                                             address=address, from_account=current_account, to_account=to_account,
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
    status_serializer = StatusFilterSerializer(data=request.query_params)
    status_serializer.is_valid(raise_exception=True)
    status_filter = status_serializer.validated_data['status'] or [0, 1]
    paginator = CountHeaderPagination()
    paginator.page_size_query_param = 'page_size'
    if current_account.is_admin:
        invoices = Invoice.objects.all().order_by('-id').filter(status__in=status_filter)
    else:
        invoices = Invoice.objects\
            .filter(Q(to_account=current_account) | Q(from_account=current_account) & Q(status__in=status_filter))\
            .order_by('-id')
    page = paginator.paginate_queryset(invoices, request)
    data = InvoiceSerializer(page, many=True).data
    return SuccessResponse(paginator.get_paginated_response(data).data, status.HTTP_200_OK)


@api_view(['PUT', 'GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def update_invoice(request, invoice_id):
    user = request.user
    try:
        invoice = Invoice.objects.get(pk=invoice_id)
    except ObjectDoesNotExist:
        return ErrorResponse(INCORRECT_ID_PATTERN.format('Заявка', invoice_id), status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return SuccessResponse(InvoiceSerializer(invoice).data, status.HTTP_200_OK)
    invoice_serializer = InvoiceSerializer(invoice, data=request.data, partial=True)
    invoice_serializer.is_valid(raise_exception=True)
    new_status = invoice_serializer.validated_data['status']
    track_id = invoice_serializer.validated_data.get('track_id', invoice.track_id)
    if track_id is None and new_status == 1 and new_status != 3:
        return ErrorResponse("Нужно указать номер трэкинга", status.HTTP_400_BAD_REQUEST)
    if new_status - invoice.status != 1 and new_status != 3:
        return ErrorResponse(INVOICE_UPDATE_ERROR, status.HTTP_400_BAD_REQUEST)
    if new_status == 2:
        to_update = []
        for product in invoice.invoice_lines.all():
            product.responsible = invoice.to_account
            product.responsible_text = invoice.to_account.get_admin_name()
            product.location_update = timezone.now()
            product.on_transition = False
            to_update.append(product)
        bulk_update(to_update, update_fields=['responsible', 'responsible_text', 'location_update', 'on_transition'])
    elif new_status == 3:
        to_update = []
        for product in invoice.invoice_lines.all():
            product.on_transition = False
            to_update.append(product)
        bulk_update(to_update, update_fields=['on_transition'])
    invoice_serializer.save()
    InvoiceChanges.objects.create(invoice=invoice, status=new_status)
    return SuccessResponse(invoice_serializer.data, status.HTTP_200_OK)

