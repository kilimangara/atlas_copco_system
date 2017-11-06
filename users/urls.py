from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^profile$', views.get_user),
    url(r'^profile/change_pass$', views.change_password),
    url(r'^auth$', views.create_user),
    url(r'^account$', views.account),
    url(r'^account/add_staff$', views.add_to_account),
    url(r'^address/(?P<address_id>\d+)$', views.get_addresses)
]