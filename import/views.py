from rest_framework import status
from rest_framework.decorators import api_view

from ara.response import SuccessResponse
from .seriliazers import XLSXImport
from products.models import Product
from users.models import Account
import openpyxl

VALID_TUPLE = ('Название', 'Наименование', 'Номер', 'Номер для заказа (10-ти значный)', 'Год выпуска', 'Кто забрал',
               'Когда', 'Комментарий')

INPUT_TYPE_FILTER_PATTERN = (None, None, None, None, None, None, None)

INPUT_TYPE = 0
PRODUCT = 1
NOTHING = 2


def valid_sheet(first_row):
    return tuple(map(lambda cell: cell.value.strip() if cell.value is not None else cell.value, first_row)) == VALID_TUPLE


def build_product_or_type_filter(row, type_filter, inner_filter, admin_account):
    if row[1:] == INPUT_TYPE_FILTER_PATTERN:
        return INPUT_TYPE, row[0].value if row[0].value is not None else NOTHING, None
    else:
        number = row[2].value if type(row[2].value) == float else '0.0'
        year = row[4].value if type(row[4].value) == int else None
        return PRODUCT, Product(title=row[0].value or '', name=row[1].value or '', number=number,
                                number_for_order=row[3].value or '', year=year,
                                responsible_text=row[5].value or '', comment=row[6].value or '',
                                type_filter=type_filter,
                                responsible=admin_account,
                                inner_type_filter=inner_filter)


@api_view(['POST'])
def import_document(request):
    serializer = XLSXImport(data=request.data)
    serializer.is_valid(raise_exception=True)
    doc = serializer.validated_data['document']
    excel_document = openpyxl.load_workbook(doc)
    admin_account = Account.objects.filter(is_admin=True).first()
    to_create = []
    for type_filter in excel_document.get_sheet_names():
        current_sheet = excel_document.get_sheet_by_name(type_filter)
        inner_type_filter = ''
        rows_tuple = tuple(current_sheet.rows)
        if not valid_sheet(rows_tuple[0]):
            continue
        for row in rows_tuple[1:]:
            res = build_product_or_type_filter(row, type_filter, inner_type_filter, admin_account)
            if res[0] == INPUT_TYPE:
                inner_type_filter = res[1]
            elif res[0] == PRODUCT:
                to_create.append(res[1])
    Product.objects.bulk_create(to_create)
    return SuccessResponse(status=status.HTTP_204_NO_CONTENT)