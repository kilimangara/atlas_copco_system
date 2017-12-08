from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^products$', views.import_document)
]