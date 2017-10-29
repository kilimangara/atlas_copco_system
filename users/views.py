from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password
from base64 import b64encode

from authentication.authentication import BasicAuthentication
from users.models import User
from users.serializers import CreateUserSerializer, UserSerializer
from ara.response import SuccessResponse, ErrorResponse


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
    user = User.objects.create(email=email, name=name, password=make_password(password), token=token)
    return SuccessResponse(UserSerializer(user).data, status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_user(request):
    if request.method == 'GET':
        return SuccessResponse(UserSerializer(request.user).data,status.HTTP_200_OK)
