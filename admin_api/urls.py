from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^users$', views.user_list),
    url(r'^products$', views.products_list),
    url(r'^accounts$', views.account_list),
    url(r'^products/(?P<product_id>\d+)$', views.crud_product),
    url(r'^users/(?P<user_id>\d+)$', views.crud_user),
    url(r'^accounts/(?P<account_id>\d+)$', views.crud_account),
]