from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password, check_password
from base64 import b64encode

from ara.error_types import NO_PERMISSION, INCORRECT_ID_PATTERN, INVALID_AUTH, ALREADY_EXIST_USER
from authentication.authentication import BasicAuthentication
from users.models import User, AccountEmailCash, Address, Account
from users.serializers import CreateUserSerializer, UserSerializer, AccountSerializer, ImportUserSerializer, \
    AddressSerializer, PasswordSerializer, LoginUserSerializer
from ara.response import SuccessResponse, ErrorResponse


def to_base64(email, password):
    basify = email + ':' + password
    return b64encode(basify.encode()).decode('utf-8')


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def all_accounts(request):
    user = request.user
    current_account = user.account
    if current_account:
        accounts = Account.objects.all().exclude(pk=current_account.id)
    else:
        accounts = Account.objects.all()
    return SuccessResponse(AccountSerializer(accounts, many=True).data, status.HTTP_200_OK)


@api_view(['POST'])
def create_user(request):
    serializer = CreateUserSerializer(data=request.data)
    if not serializer.is_valid():
        return ErrorResponse(serializer.errors_to_text, status.HTTP_400_BAD_REQUEST)
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    name = serializer.validated_data['name']
    token = to_base64(email, password)
    cash_account = AccountEmailCash.objects.filter(email=email).first()
    account = cash_account.account if cash_account is not None else None
    if User.objects.filter(email=email).first():
        return ErrorResponse(ALREADY_EXIST_USER, status.HTTP_400_BAD_REQUEST)
    else:
        user = User.objects.create(email=email, name=name, password=make_password(password), token=token, account=account)
        return SuccessResponse(UserSerializer(user).data, status.HTTP_201_CREATED)


@api_view(['POST'])
def login_user(request):
    serializer = LoginUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    existed_user = User.objects.filter(email=email).first()
    if existed_user:
        if check_password(password, existed_user.password):
            return SuccessResponse(UserSerializer(existed_user).data, status.HTTP_201_CREATED)
        else:
            return ErrorResponse(INVALID_AUTH, status.HTTP_400_BAD_REQUEST)
    else:
        return ErrorResponse(INVALID_AUTH, status.HTTP_400_BAD_REQUEST)


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


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    password_serializer = PasswordSerializer(data=request.data)
    if not password_serializer.is_valid():
        return ErrorResponse(password_serializer.errors_to_text, status.HTTP_400_BAD_REQUEST)
    password = password_serializer.validated_data['password']
    user.password = make_password(password)
    user.token = to_base64(user.email, password)
    user.save()
    return SuccessResponse(UserSerializer(user).data, status.HTTP_200_OK)


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
        if current_account.address is not None:
            address_serializer = AddressSerializer(current_account.address, data=request.data, partial=True)
        else:
            address_serializer = AddressSerializer(data=request.data)
        address_serializer.is_valid(raise_exception=True)
        address = address_serializer.save()
        current_account.address = address
        account_serializer = AccountSerializer(current_account, data=request.data, partial=True)
        account_serializer.is_valid(raise_exception=True)
        account_serializer.save()
        return SuccessResponse(account_serializer.data, status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def single_account(request, pk):
    if request.method == 'GET':
        try:
            pk_account = Account.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return ErrorResponse(INCORRECT_ID_PATTERN.format('Филиал', pk), status.HTTP_404_NOT_FOUND)
        return SuccessResponse(AccountSerializer(pk_account).data, status.HTTP_200_OK)


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


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_addresses(request, address_id):
    try:
        address = Address.objects.get(pk=address_id)
    except ObjectDoesNotExist:
        return ErrorResponse(INCORRECT_ID_PATTERN.format('Адрес', address_id), status.HTTP_404_NOT_FOUND)
    return SuccessResponse(AddressSerializer(address).data, status.HTTP_200_OK)

