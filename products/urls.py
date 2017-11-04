from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^filters', views.get_filters),
    url(r'^all', views.show_products),
    url(r'^(?P<product_id>\d+)', views.show_product),
    url(r'^invoice', views.create_invoice),
    url(r'^check_invoice', views.check_invoice)
]