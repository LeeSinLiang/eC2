from django.contrib import admin
from .models import Product, Variation, ProductImage, Category, ProductFeatured, Brand

class InlineProductImage(admin.StackedInline):
    model = ProductImage
    fieldsets =(
        (None, {
            'fields': (
                'product',
                'image'
            )
        }),
    )
    extra = 1
    max_num = 5

class InlineVariation(admin.StackedInline):
    model = Variation
    fieldsets =(
        (None, {
            'fields': (
                'product',
                'title',
                'price',
                'sale_price',
                'active',
                'inventory',
                'sold_bill'
            )
        }),
    )
    extra = 1
    max_num = 5

class ProductModelAdmin(admin.ModelAdmin):
    inlines = [InlineProductImage, InlineVariation]
    list_display = ["title", "price"]
    class Meta:
        model = Product

# Register your models here.
admin.site.site_header = "eC2 Administration"
admin.site.site_title = "eC2 Administration"

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product, ProductModelAdmin)
admin.site.register(ProductImage)
admin.site.register(ProductFeatured)