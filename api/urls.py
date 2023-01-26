""" urls for the substances app """
from django.urls import path
from api import views


urlpatterns = [
    path("", views.home, name='index'),
    path("units/<uid>", views.units, name='json'),
]
