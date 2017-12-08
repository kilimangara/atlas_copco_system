from rest_framework import serializers


class XLSXImport(serializers.Serializer):
    document = serializers.FileField()