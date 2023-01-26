""" urls for the representations app """
from django.urls import path
from api import views


urlpatterns = [
    path("", views.home, name='index'),
    path("calculate/<usrkey>/<uid>", views.units, name='json'),
]
