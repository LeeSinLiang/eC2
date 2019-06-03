from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from .views import *
from django.urls import path

urlpatterns = [
    path('', CategoryListView.as_view(), name='categories'),
    path('<int:pk>/', CategoryDetailView.as_view(), name='category_detail_id'),
    path('<slug>/', SubCategoryListView.as_view(), name='subcategory'),
    path('<id>/<slug>/', CategoryDetailView.as_view(), name='category_detail'),
]