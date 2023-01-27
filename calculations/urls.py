""" urls for the representations app """
from django.urls import path
from calculations import views


urlpatterns = [
    path("", views.index, name='index'),
    path("calculate/<usrkey>/<uid>", views.calculate, name='json'),
    path("compute", views.compute, name='compute'),
]
