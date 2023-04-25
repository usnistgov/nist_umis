""" urls for the substances app """
from django.urls import path
from quantitykinds import views


urlpatterns = [
    path("", views.index, name='index'),
    path("view/<qkid>", views.view, name='view'),
]
