from __future__ import absolute_import, unicode_literals
from celery import task
from django.core.mail import send_mail

from .models import Invoice
from users.models import Account


@task
def check_invoice_status(invoice_id):
    invoice = Invoice.objects.where(pk=invoice_id).first
    if invoice and invoice.status == 1:
        from_account_emails = invoice.from_account.get_admins_emails()
        to_account_email = invoice.to_account.get_admins_emails()
        admin_email = Account.objects.filter(is_admin=True).first().get_admins_emails()
        merged_list = list(set(from_account_emails + to_account_email + admin_email))
        send_mail('Заявка №{} долго не меняет статус'.format(invoice.id),
                  'Просим обратить внимание и поменять статус заявки', 'kilimangara@yandex.ru', merged_list,
                  fail_silently=True)


@task
def send_notification(invoice_id):
    invoice = Invoice.objects.where(pk=invoice_id).first
    if invoice:
        from_account_emails = invoice.from_account.get_admins_emails
        to_account_email = invoice.to_account.get_admins_emails
        admin_email = Account.objects.filter(is_admin=True).first().get_admins_emails()
        merged_list = list(set(from_account_emails + to_account_email + admin_email))
        send_mail('Новая заявка №{}'.format(invoice.id),
                  'Создана новая заявка', 'kilimangara@yandex.ru', merged_list,
                  fail_silently=True)