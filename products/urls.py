from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^all', views.products),
    url(r'^(?P<product_id>\d+)', views.product)
]