from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^profile', views.get_user),
    url(r'^auth', views.create_user)
]