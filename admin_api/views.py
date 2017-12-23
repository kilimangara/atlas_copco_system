from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from admin_api.permissions import AdminPermission
from ara.response import SuccessResponse, ErrorResponse
from authentication.authentication import BasicAuthentication
from products.models import Product
from users.models import Account, User
from .serializers import AccountSerializer, UserSerializer, ProductSerializer


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated, AdminPermission])
def account_list(request):
    return SuccessResponse(AccountSerializer(Account.objects.all(), many=True).data, status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated, AdminPermission])
def user_list(request):
    users = User.objects.all().exclude(pk=request.user.id)
    return SuccessResponse(UserSerializer(users, many=True), status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated, AdminPermission])
def products_list(request):
    return SuccessResponse(ProductSerializer(Product.objects.all(), many=True), status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated, AdminPermission])
def crud_user(request, user_id):
    try:
        user = User.objects.find(pk=user_id)
    except ObjectDoesNotExist:
        return ErrorResponse('Нет такого пользователя', status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        return SuccessResponse(UserSerializer(user), status.HTTP_200_OK)
    elif request.method == 'DELETE':
        user.delete()
        return SuccessResponse(status=status.HTTP_204_NO_CONTENT)
    else:
        user_serializer = UserSerializer(user, data=request.data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        return SuccessResponse(user_serializer.data, status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated, AdminPermission])
def crud_product(request, product_id):
    try:
        product = Product.objects.find(pk=product_id)
    except ObjectDoesNotExist:
        return ErrorResponse('Нет такого инструмента', status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        return SuccessResponse(ProductSerializer(product), status.HTTP_200_OK)
    elif request.method == 'DELETE':
        product.delete()
        return SuccessResponse(status=status.HTTP_204_NO_CONTENT)
    else:
        serializer = ProductSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return SuccessResponse(serializer.data, status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated, AdminPermission])
def crud_account(request, account_id):
    try:
        account = Account.objects.find(pk=account_id)
    except ObjectDoesNotExist:
        return ErrorResponse('Нет такого филиала', status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        return SuccessResponse(AccountSerializer(account), status.HTTP_200_OK)
    elif request.method == 'DELETE':
        account.delete()
        return SuccessResponse(status=status.HTTP_204_NO_CONTENT)
    else:
        serializer = AccountSerializer(account, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return SuccessResponse(serializer.data, status.HTTP_200_OK)

