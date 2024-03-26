from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('mint/', mint, name='mint'),
    path('tickets/', tickets, name='tickets'),
    path('info/', info, name='info'),
]