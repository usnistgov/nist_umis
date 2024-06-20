""" urls for the dashboard app """
from django.urls import path
from . import views


urlpatterns = [
    path("", views.overview, name='overview'),
    path("dashajax", views.dashajax, name='ajax'),
]
