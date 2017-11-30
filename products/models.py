from django.db import models

STATUSES = (
    (0, 'Создано'),
    (1, 'В обработке'),
    (2, 'Отдано курьерам'),
    (3, 'Принято от курьера'),
    (4, 'Закрыто')
)

TARGETS = (
    (0, 'Выставка'),
    (1, 'Демонстрация'),
    (2, 'Семинар'),
    (3, 'Возврат')
)


class Product(models.Model):
    title = models.CharField(max_length=255)
    sku = models.CharField(max_length=255, unique=True)
    number = models.FloatField(blank=True)
    number_for_order = models.CharField(max_length=10)
    year = models.IntegerField(null=True, blank=True)
    responsible = models.ForeignKey('users.Account', models.CASCADE, related_name='products', null=True, blank=True)
    responsible_text = models.CharField(max_length=255, null=True, blank=True)
    on_transition = models.BooleanField(default=False)
    location_update = models.DateTimeField(null=True)
    comment = models.CharField(max_length=255, blank=True)
    on_repair = models.BooleanField(default=False)
    type_filter = models.CharField(max_length=255, null=True, default='', db_index=True, blank=True)

    def __str__(self):
        return '{} {}'.format(self.title, self.sku)


class InvoiceChanges(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    invoice = models.ForeignKey('Invoice', models.CASCADE, related_name='invoice_changes')
    status = models.IntegerField(choices=STATUSES)


class Invoice(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    invoice_lines = models.ManyToManyField('Product')
    comment = models.CharField(max_length=255)
    address = models.ForeignKey('users.Address')
    invoice_type = models.IntegerField(choices=TYPES, default=0)
    from_account = models.ForeignKey('users.Account', models.CASCADE, related_name='out_invoices')
    to_account = models.ForeignKey('users.Account', models.CASCADE, related_name='in_invoices')
    target = models.IntegerField(choices=TARGETS, null=True)
    status = models.IntegerField(choices=STATUSES, default=0)

    def __str__(self):
        return '{}.От {} К {}'.format(self.id, self.from_account, self.to_account)
