from django.urls import path
from .views import *

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('count/', ItemCountView.as_view(), name='item_count'),
]