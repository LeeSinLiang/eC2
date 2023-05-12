from django_filters import FilterSet, CharFilter, NumberFilter

from .models import Product

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