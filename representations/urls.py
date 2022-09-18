""" urls for the substances app """
from django.urls import path
from representations import views


urlpatterns = [
    path("", views.index, name='index'),
    path("view/<rid>", views.view, name='view'),
]
