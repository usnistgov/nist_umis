""" urls for the substances app """
from django.urls import path
from domains import views


urlpatterns = [
    path("", views.index, name='index'),
]
