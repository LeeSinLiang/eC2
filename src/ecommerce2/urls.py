from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from newsletter.views import *
from ecommerce2.views import *
from django.urls import path, include
from carts.views import *
from orders.views import *
from utily.views import WishListView, wishlisted
from products.views import (
    CategoryListAPIView,
    CategoryDetailAPIView,
)

urlpatterns = [
    # Examples:
    path('', home, name='home'),
    url(r'^contact/$', contact, name='contact'),
    url(r'^about/$', about, name='about'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('registration.backends.default.urls')),
    path('category/', include('products.urls_categories')),
    path('carts/', include('carts.urls')),
    path('checkout/address/', AddressSelectFormView.as_view(), name='order_address'),
    path('checkout/add/', UserAddressCreateView.as_view(), name='user_address_create'),
    path('checkout/final/', CheckoutFinalView.as_view(), name='checkout_final'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', OrderList.as_view(), name='orders'),
    path('orders/<pk>/', OrderDetail.as_view(), name='order_detail'),
    path('products/', include('products.urls')),
    path('wishlist/', WishListView.as_view(), name='wishlist'),
    path('wishlist/<int:pk>/', wishlisted, name='wishlisted'),

]

urlpatterns += [
    path('api/categories/', CategoryListAPIView.as_view(), name='categories_api'),
    path('api/categories/<pk>/', CategoryDetailAPIView.as_view(), name='category_detail_api'),
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)