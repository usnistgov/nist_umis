""" urls for the substances app """
from django.urls import path
from vectors import views


urlpatterns = [
    path("", views.index, name='index'),
    path("view/<dvid>", views.view, name='view'),
]
