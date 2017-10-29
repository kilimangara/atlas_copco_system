from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password
from base64 import b64encode

from ara.error_types import NO_PERMISSION
from authentication.authentication import BasicAuthentication
from users.models import User, AccountEmailCash
from users.serializers import CreateUserSerializer, UserSerializer, AccountSerializer, ImportUserSerializer
from ara.response import SuccessResponse, ErrorResponse
from .permissions import AdminUserPermission


def to_base64(email, password):
    basify = email + ':' + password
    return b64encode(basify.encode('ascii')).decode('utf-8')


@api_view(['POST'])
def create_user(request):
    serializer = CreateUserSerializer(data=request.data)
    if not serializer.is_valid():
        return ErrorResponse(serializer.errors_to_text, status.HTTP_400_BAD_REQUEST)
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    name = serializer.validated_data['name']
    token = to_base64(email, password)
    cash_account = AccountEmailCash.objects.get(email=email)
    account = cash_account.account if cash_account is not None else None
    user = User.objects.create(email=email, name=name, password=make_password(password), token=token, account=account)
    return SuccessResponse(UserSerializer(user).data, status.HTTP_201_CREATED)


@api_view(['GET', 'PUT'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_user(request):
    if request.method == 'GET':
        return SuccessResponse(UserSerializer(request.user).data, status.HTTP_200_OK)
    elif request.method == 'PUT':
        user = request.user
        user_serializer = UserSerializer(user, data=request.data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        return SuccessResponse(user_serializer.data, status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def account(request):
    user = request.user
    current_account = user.account
    if request.method == 'GET':
        return SuccessResponse(AccountSerializer(current_account).data, status.HTTP_200_OK)
    if request.method == 'PUT':
        if not user.is_admin:
            return ErrorResponse(NO_PERMISSION, status.HTTP_403_FORBIDDEN)
        account_serializer = AccountSerializer(current_account, data=request.data, partial=True)
        account_serializer.is_valid(raise_exception=True)
        account_serializer.save()
        return SuccessResponse(account_serializer.data, status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def add_to_account(request):
    user = request.user
    current_account = user.account
    if not user.is_admin:
        return ErrorResponse(NO_PERMISSION, status.HTTP_403_FORBIDDEN)
    import_serializer = ImportUserSerializer(data=request.data)
    import_serializer.is_valid(raise_exception=True)
    added = current_account.add_user(import_serializer.validated_data['email'])
    return SuccessResponse({'status': added}, status.HTTP_200_OK)

