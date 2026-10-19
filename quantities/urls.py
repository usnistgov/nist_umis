""" urls for the substances app """
from django.urls import path
from quantities import views


urlpatterns = [
    path("", views.index, name='quantity index'),
    path("view/<qid>", views.view, name='quantity view'),
]
