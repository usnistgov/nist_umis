""" urls for the substances app """
from django.urls import path
from quantitysystems import views


urlpatterns = [
    path("", views.index, name='index'),
    path("view/<qsid>", views.view, name='view'),
]
