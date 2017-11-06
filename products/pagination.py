from collections import OrderedDict

from rest_framework import pagination
from rest_framework.response import Response


class CountHeaderPagination(pagination.PageNumberPagination):

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.num_pages),
            ('results', data)
        ]))
