from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.core.exceptions import *
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from products.models import Product
import json
from orders.mixins import LoginRequiredMixin
from .models import Wishlist

# Create your views here.


class WishListView(LoginRequiredMixin, ListView):
    model = Wishlist
    http_method_names = ['delete', 'get', 'post']
    template_name = 'utily/wishlist/wishlistview.html'

    def get_queryset(self, *args, **kwargs):
        queryset = super(WishListView, self).get_queryset(*args, **kwargs)
        queryset.filter(user=self.request.user)
        return queryset

    def delete(self, *args, **kwargs):
        id = json.loads(self.request.body)['id']
        wishlist = get_object_or_404(Wishlist, id=id)
        wishlist.delete()

        return HttpResponse('')

    # def get(self, request, *args, **kwargs):
    #     product = request.GET.get('item')
    #     print(product)
    #     delete = request.GET.get('delete', False)
    #     print(delete)
    #     # if product
    #     #     if delete == True:
    #     wishlist_product = Wishlist.objects.get(
    #         user=self.request.user, product=product)
    #     print(wishlist_product)
    #     wishlist_product.delete()
    #     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    #     try:
    #         queryset123 = self.get_queryset()

    #     except:
    #         queryset123 = None

    #     print(queryset123)
    #     # except ObjectDoesNotExist:
    #     #     messages.warning(self.request, 'Oops, This product does not exists')

    #     return render(request, self.template_name, {'object_list': queryset123})


def wishlisted(request, pk):
    # try:
    product = Product.objects.get(pk=pk)
    wishlist = Wishlist.objects.create(user=request.user, product=product)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    # except ObjectDoesNotExist or EmptyResultSet:
    #     pass
