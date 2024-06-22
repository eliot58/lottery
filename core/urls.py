from django.urls import path
from .views import *

urlpatterns = [
    path('getWallets/<str:address>/', getWallets)
]