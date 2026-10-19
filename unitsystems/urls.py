""" urls for the substances app """
from django.urls import path
from unitsystems import views


urlpatterns = [
    path("", views.index, name='unit system index'),
    path("view/<usid>", views.view, name='unit system view'),
]
