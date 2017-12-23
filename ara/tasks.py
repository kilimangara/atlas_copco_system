from celery import task

from products.models import Invoice


@task(bind=True, default_retry_delay=300, max_retries=5)
def check_invoice(invoice_id):
    invoice = Invoice.objects.where(pk=invoice_id).first
