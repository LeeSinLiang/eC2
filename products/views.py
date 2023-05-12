import random
import pdb
from django.db.models import Q
from django.shortcuts import render, _get_queryset
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormMixin
from .models import Product, Variation, Category
from .forms import VariationInventoryFormSet, ProductFilterForm, CategoryFilterForm
from utily.forms import *
from utily.models import *
from orders.mixins import CartOrderMixin
from orders.models import Order, UserCheckout
from utily.models import History
from .mixins import StaffRequiredMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ImproperlyConfigured
from django_filters import FilterSet, CharFilter, NumberFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import FieldError
from django.utils import timezone
from django.contrib import messages
from .filters import ProductFilter
from .pagination import ProductPagination, CategoryPagination
# Create your views here.
from rest_framework import (
    generics,
    filters
)

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.reverse import reverse as api_reverse

from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductDetailSerializer,
)

class APIHomeView(APIView):
	# authentication_classes = [SessionAuthentication]
	# permission_classes = [IsAuthenticated]
	def get(self, request, format=None):
		data = {
			# "auth": {
			# 	"login_url":  api_reverse("auth_login_api", request=request),
			# 	"refresh_url":  api_reverse("refresh_token_api", request=request),
			# 	"user_checkout":  api_reverse("user_checkout_api", request=request),
			# },
			# "address": {
			# 	"url": api_reverse("user_address_list_api", request=request),
			# 	"create":   api_reverse("user_address_create_api", request=request),
			# },
			# "checkout": {
			# 	"cart": api_reverse("cart_api", request=request),
			# 	"checkout": api_reverse("checkout_api", request=request),
			# 	"finalize": api_reverse("checkout_finalize_api", request=request),
			# },
			"products": {
				"count": Product.objects.all().count(),
				"url": api_reverse("products_api", request=request)
			},
			"categories": {
				"count": Category.objects.all().count(),
				"url": api_reverse("categories_api", request=request)
			},
			# "orders": {
			# 	"url": api_reverse("orders_api", request=request),
			# }
		}
		return Response(data)

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CategoryPagination


class CategoryDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductListAPIView(generics.ListAPIView):
    # authentication_classes = [SessionAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend
    ]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "id"]
    filter_class = ProductFilter
    pagination_class = ProductPagination


class ProductRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer


class FilterMixin(object):
    filter_class = None
    search_ordering_param = "ordering"

    def get_queryset(self, *args, **kwargs):
        try:
            qs = super(FilterMixin, self).get_queryset(*args, **kwargs)
            return qs
        except:
            pass

    def get_object(self, *args, **kwargs):
        try:
            obj = super(FilterMixin, self).get_object(*args, **kwargs)
            return obj
        except:
            pass

    def get_context_data(self, *args, **kwargs):
        context = super(FilterMixin, self).get_context_data(*args, **kwargs)
        qs = self.get_queryset()
        obj = self.get_object()
        if obj:
            product_set = obj.product_set.all()
            default_products = obj.default_category.all()
            qs = (product_set | default_products).distinct()

        ordering = self.request.GET.get(self.search_ordering_param)
        if ordering:
            qs = qs.order_by(ordering)
        filter_class = self.filter_class
        if filter_class:
            f = filter_class(self.request.GET, queryset=qs)
            fqs = f.qs
        query = self.request.GET.get("q")
        sort = self.request.GET.get("sort")
        if query and sort:
            try:
                fqs = fqs.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query)
                ).order_by(sort)
            except FieldError:
                pass

        elif sort:
            try:
                fqs = fqs.order_by(sort)
            except:
                pass

        elif query:
            fqs = fqs.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
        context['object_list'] = fqs
        return context


class CategoryFilter(FilterSet):
    title = CharFilter(field_name='title',
                       lookup_expr='icontains', distinct=True)
    brand = CharFilter(field_name='brand__title',
                       lookup_expr='icontains', distinct=True)
    brand_id = CharFilter(field_name='brand__id',
                          lookup_expr='icontains', distinct=True)
    # (some_price__gte=somequery)
    min_price = NumberFilter(field_name='variation__sale_price',
                             lookup_expr='gte', distinct=True)
    max_price = NumberFilter(field_name='variation__sale_price',
                             lookup_expr='lte', distinct=True)

    class Meta:
        model = Product
        fields = [
            'min_price',
            'max_price',
            'brand',
            'title',
        ]


class CategoryListView(ListView):
    model = Category
    template_name = "products/category_list.html"

    def get_queryset(self, *args, **kwargs):
        qs = super(CategoryListView, self).get_queryset(*args, **kwargs)
        qs = qs.filter(parent=None)
        return qs


class SubCategoryListView(ListView):
    model = Category
    template_name = "products/category_list.html"

    def get_queryset(self, *args, **kwargs):
        qs = super(SubCategoryListView, self).get_queryset(*args, **kwargs)
        category_parent = Category.objects.get(slug=self.kwargs.get('slug'))
        qs = qs.filter(parent=category_parent)
        return qs


class CategoryDetailView(FilterMixin, DetailView):
    model = Category
    template_name = "products/category_detail.html"
    filter_class = CategoryFilter

    def get_object(self, *args, **kwargs):
        obj = None
        if self.kwargs.get('pk') is not None and self.kwargs.get('slug') is not None:
            slug = self.kwargs.get('slug')
            obj = Category.objects.get(slug=slug)

        elif self.kwargs.get('pk') is not None:
            pk = self.kwargs.get('pk')
            obj = Category.objects.get(id=pk)

        elif self.kwargs.get('slug') is not None:
            slug = self.kwargs.get('slug')
            obj = Category.objects.get(slug=slug)

        return obj

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(
            *args, **kwargs)
        obj = self.get_object()
        product_set = obj.product_set.all()
        default_products = obj.default_category.all()
        qs = (product_set | default_products).distinct()
        sort = self.request.GET.get("sort")
        if sort:
            try:
                qs = qs.order_by(sort)
            except FieldError:
                pass

        context["filter_form"] = CategoryFilterForm(
            data=self.request.GET or None)
        context["object_list1"] = qs
        return context


class VariationListView(StaffRequiredMixin, ListView):
    model = Variation
    template_name = "products/variation_list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(VariationListView, self).get_context_data(
            *args, **kwargs)
        context["formset"] = VariationInventoryFormSet(
            queryset=self.get_queryset())
        return context

    def get_queryset(self, *args, **kwargs):
        product_slug = self.kwargs.get('slug')
        product_id = self.kwargs.get('id')
        if product_id and product_slug:
            product = get_object_or_404(
                Product, slug=product_slug, id=product_id)
            queryset = Variation.objects.filter(product=product)
        return queryset

    def post(self, request, *args, **kwargs):
        formset = VariationInventoryFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save(commit=False)
            for form in formset:
                new_item = form.save(commit=False)
                product_slug = self.kwargs.get("slug")
                product_id = self.kwargs.get("id")
                product = get_object_or_404(
                    Product, slug=product_slug, id=product_id)
                new_item.product = product
                new_item.save()

            messages.success(
                request, "Your inventory and pricing has been updated.")
            return redirect("products:products")
        raise Http404


class ProductFilter(FilterSet):
    title = CharFilter(field_name='title',
                       lookup_expr='icontains', distinct=True)
    category = CharFilter(field_name='categories__title',
                          lookup_expr='icontains', distinct=True)
    category_id = CharFilter(field_name='categories__id',
                             lookup_expr='icontains', distinct=True)
    brand = CharFilter(field_name='brand__title',
                       lookup_expr='icontains', distinct=True)
    brand_id = CharFilter(field_name='brand__id',
                          lookup_expr='icontains', distinct=True)
    # (some_price__gte=somequery)
    min_price = NumberFilter(field_name='variation__sale_price',
                             lookup_expr='gte', distinct=True)
    max_price = NumberFilter(field_name='variation__sale_price',
                             lookup_expr='lte', distinct=True)

    class Meta:
        model = Product
        fields = [
            'min_price',
            'max_price',
            'brand',
            'category',
            'title',
        ]


class ProductFilter123(FilterSet):
    class Meta:
        model = Product
        fields = ['title', 'description']


def product_list(request):
    qs = Product.objects.all()
    ordering = request.GET.get("ordering")
    if ordering:
        qs = Product.objects.all().order_by(ordering)
    f = ProductFilter(request.GET, queryset=Product.objects.all())
    return render(request, "products/product_list.html", {"object_list": f.qs})


class ProductListView(FilterMixin, ListView):
    model = Product
    queryset = Product.objects.filter(active=True)
    template_name = "products/product_list.html"
    filter_class = ProductFilter

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(
            *args, **kwargs)
        # context['object_list'] = Product.objects.filter(active=True)
        # context['object_list'] = self.get_queryset()
        context["query"] = self.request.GET.get("q")
        context["filter_form"] = ProductFilterForm(
            data=self.request.GET or None)
        return context

    def get_queryset(self, *args, **kwargs):
        qs = super(ProductListView, self).get_queryset(*args, **kwargs)
        query = self.request.GET.get("q")
        sort = self.request.GET.get("sort")
        if query and sort:
            try:
                qs = self.model.objects.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query)
                ).order_by(sort)
            except FieldError:
                pass
            try:
                qs2 = self.model.objects.filter(
                    Q(price=query)
                ).order_by(sort)
                qs = (qs | qs2).distinct()
            except FieldError:
                pass

        elif sort:
            try:
                qs = self.model.objects.order_by(sort)
            except FieldError:
                pass

        elif query:
            qs = self.model.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
            try:
                qs2 = self.model.objects.filter(
                    Q(price=query)
                )
                qs = (qs | qs2).distinct()
            except:
                pass
        return qs


class ProductDetailView(CartOrderMixin, DetailView):
    model = Product
    template_name = "products/product_detail.html"
    # form_class = ReviewForm

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(
            *args, **kwargs)
        instance = self.get_object()
        context["related"] = sorted(Product.objects.get_related(instance)[
                                    :3], key=lambda x: random.random())
        context['review'] = Review.objects.filter(
            product=self.get_object()).order_by('-pk')
        form = ReviewForm(self.request.POST)
        history = self.request.session.get("history_ids")
        if history is None:
            self.request.session["history_ids"] = []
        self.request.session["history_ids"].append(self.get_object().id)

        try:
            user = UserCheckout.objects.get(user=self.request.user)
        except:
            user = None
        order = Order.objects.filter(user=user)
        product = self.get_object()

        for o in order:
            if o.status == 'paid':
                for p in product.variation_set.all():
                    for item123 in o.cart.items.all():
                        if item123.pk == p.pk:
                            context['form'] = form
                            break
                            break
                            break
            else:
                context['form'] = None
        # print(Product.objects.get_related(instance))
        return context

    def post(self, *args, **kwargs):
        order = self.get_order()
        ratings = self.request.POST['rating']
        content = self.request.POST['content']
        vp = False
        if order is not None:
            if order.status == 'paid':
                vp = True

        review, created = Review.objects.get_or_create(
            user=self.request.user, ratings=ratings, product=self.get_object(),  verified_purchase=vp, content=content)
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))

    def form_valid(self, *args, **kwargs):

        return super(ReviewForm, self).form_valid(form, *args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))


def product_detail_view_func(request, slug, id):
        # product_instance = Product.objects.get(id=id)
    product_instance = get_object_or_404(Product, slug=slug)
    try:
        product_instance = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        raise Http404
    except:
        raise Http404

    template = "products/product_detail.html"
    context = {
        "object": product_instance
    }
    return render(request, template, context)
