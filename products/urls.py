from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from .views import *
from django.urls import path

app_name = 'products'

urlpatterns = [
    # Examples:
    # path('', product_list, name='products'),
    path('', ProductListView.as_view(), name='products'),
    path('<slug>/<int:id>/', ProductDetailView.as_view(), name='product_detail'),
    path('<slug>/<int:id>/inventory/', VariationListView.as_view(), name='product_inventory'),
    # path('<slug>/<int:id>/', product_detail_view_func, name='product_detail'),
]