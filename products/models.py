from datetime import datetime, timedelta

from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django_bulk_update.helper import bulk_update

STATUSES = (
    (0, 'В обработке'),
    (1, 'Отдано курьерам'),
    (2, 'Принято от курьера'),
    (3, 'Закрыто')
)

TYPES = (
    (0, 'Получение'),
    (1, 'Отправка'),
    (2, 'Ремонт')
)

TARGETS = (
    (0, 'Выставка'),
    (1, 'Демонстрация'),
    (2, 'Семинар'),
    (3, 'Возврат')
)


class Product(models.Model):
    title = models.CharField(max_length=255, default='')
    name = models.CharField(max_length=255, default='')
    number = models.FloatField(blank=True, default=0.0)
    number_for_order = models.CharField(max_length=255, blank=True, null=True)
    year = models.IntegerField(null=True, blank=True)
    responsible = models.ForeignKey('users.Account', models.CASCADE, related_name='products', null=True, blank=True)
    responsible_text = models.CharField(max_length=255, null=True, blank=True)
    on_transition = models.BooleanField(default=False)
    location_update = models.DateTimeField(null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)
    on_repair = models.BooleanField(default=False)
    type_filter = models.CharField(max_length=255, null=True, default='', db_index=True, blank=True)
    inner_type_filter = models.CharField(max_length=255, null=True, default='', db_index=True, blank=True)

    def __str__(self):
        return '{} {}'.format(self.title, self.name)


class InvoiceChanges(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    invoice = models.ForeignKey('Invoice', models.CASCADE, related_name='invoice_changes')
    status = models.IntegerField(choices=STATUSES)


class Invoice(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    track_id = models.CharField(max_length=255, null=True)
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


@receiver(pre_save, sender=Product)
def product_changed(instance, **kwargs):
    if instance.responsible:
        instance.responsible_text = instance.responsible.get_admin_name()


@receiver(post_save, sender=Invoice)
def new_invoice(created, instance, **kwargs):
    if instance.status == 1:
        time_to_check = datetime.utcnow() + timedelta(days=5)
        from .tasks import check_invoice_status
        check_invoice_status.apply_async((instance.id,), eta=time_to_check)
    if instance.status == 0 and len(instance.invoice_lines.all()) != 0:
        to_update = []
        from .tasks import send_notification
        send_notification.delay(instance.id)
        for product in instance.invoice_lines.all():
            product.on_transition = True
            to_update.append(product)
        bulk_update(to_update, update_fields=['on_transition'])
