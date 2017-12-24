from __future__ import absolute_import, unicode_literals
from celery import task
from django.core.mail import send_mail


@task
def send_invite(email):
    send_mail('Вы приглашены в систему учета AtlasCopco', 'Просим зарегестрироваться по ссылке',
              'kilimangara@yandex.ru',[email], fail_silently=True)