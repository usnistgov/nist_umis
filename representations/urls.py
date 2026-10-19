""" urls for the representations app """
from django.urls import path
from representations import views


urlpatterns = [
    path("", views.index, name='representation index'),
    path("view/<rid>", views.view, name='representation view'),
]
