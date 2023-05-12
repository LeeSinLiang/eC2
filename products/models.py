from django.db import models
from django.urls import reverse
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from django.core.signing import Signer
# Create your models here.


class ProductQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    # def all(self, *args, **kwargs):
    #     return self.get_queryset().active()

    def get_related(self, instance):
        products_one = self.get_queryset().filter(
            categories__in=instance.categories.all())
        products_two = self.get_queryset().filter(default=instance.default)
        qs = (products_one | products_two).exclude(id=instance.id).distinct()
        return qs


class Product(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=1000)
    active = models.BooleanField()
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, null=True)
    categories = models.ManyToManyField('Category', blank=True)
    default = models.ForeignKey('Category', related_name='default_category',
                                null=True, blank=True, on_delete=models.SET_NULL)

    inventory = models.IntegerField()
    objects = ProductManager()

    def save(self, *args, **kwargs):
        super(Product, self).save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(self.title)
            self.qs = Product.objects.filter(
                slug=self.slug).order_by("-id")
            self.exists = self.qs.exists()
            if self.exists:
                self.new_slug = "%s-%s" % (self.slug, self.qs.first().id)
                self.slug = self.new_slug
            self.save()

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug, 'id': self.id})

    def get_image_url(self):
        img = self.productimage_set.first()
        if img:
            return img.image.url
        return img

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-id']


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    price = models.DecimalField(decimal_places=2, max_digits=20)
    sale_price = models.DecimalField(
        decimal_places=2, max_digits=20, null=True, blank=True)
    active = models.BooleanField(default=True)
    inventory = models.IntegerField()
    sold_bill = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        super(Variation, self).save(*args, **kwargs)
        if self.sale_price is None:
            self.sale_price = self.price
            self.save()


    def __str__(self):
        return self.title

    def get_price(self):
        if self.sale_price != self.price and self.sale_price is not None:
            return self.sale_price
        else:
            return self.price

    def get_absolute_url(self):
        return self.product.get_absolute_url()

    def get_html_price(self):
        if self.sale_price != self.price and self.sale_price is not None:
            html_text = "<span class='sale-price'>%s</span> <span class='og-price'>%s</span>" % (
                self.sale_price, self.price)
        else:
            html_text = "<span class='price'>%s</span>" % (self.price)
        return mark_safe(html_text)

    def add_to_cart(self):
        return "%s?item=%s&qty=1" % (reverse("cart"), self.id)

    def remove_from_cart(self):
        return "%s?item=%s&qty=1&delete=True" % (reverse("cart"), self.id)

    def get_title(self):
        return "%s - %s" % (self.product.title, self.title)


def product_saved_receiver(sender, instance, created, *args, **kwargs):
    product = instance
    variations = product.variation_set.all()
    if variations.count() == 0:
        new_var = Variation()
        new_var.product = product
        new_var.title = "Default"
        new_var.price = product.price
        new_var.inventory = product.inventory
        new_var.save()


post_save.connect(product_saved_receiver, sender=Product)


def image_upload_to(instance, filename):
    title = instance.product.title
    idd = instance.product.id
    slug = slugify(title)
    basename, file_extension = filename.split(".")
    new_filename = "%s.%s" % (slug, file_extension)
    return "products/%s/%s/%s" % (slug, idd, new_filename)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_to)

    def __str__(self):
        return self.product.title


def image_upload_to_category(instance, filename):
    if instance.parent is None:
        title = instance.title
        slug = title
    else:
        title = instance.title
        id1 = instance.parent.id
        slug = '%s/%s' % (title, id1)

    basename, file_extension = filename.split(".")
    new_filename = "%s.%s" % (instance.slug, file_extension)
    return "%s/%s" % (slug, new_filename)

class Category(models.Model):
    title = models.CharField(max_length=120, unique=True)
    background_image = models.ImageField(upload_to=image_upload_to_category, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    parent = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    brand = models.ManyToManyField('Brand', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(self.title)
            self.qs = Category.objects.filter(
                slug=self.slug).order_by("-id")
            self.exists = self.qs.exists()
            if self.exists:
                self.new_slug = "%s-%s" % (self.slug, self.qs.first().id)
                self.slug = self.new_slug
            self.save()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # if self.category_set.all().count() < 1:
        #     return reverse('category_detail_id', kwargs={'id': self.id})
        # else:
        return reverse('subcategory', kwargs={'slug': self.slug})


def image_upload_to_brand(instance, filename):
    title = instance.title
    return 'brand/%s/%s' % (title, filename)

class Brand(models.Model):
    title = models.CharField(max_length=250)
    image = models.ImageField(upload_to=image_upload_to_brand)

    def __str__(self):
        return self.title

def image_upload_to_featured(instance, filename):
    title = instance.product.title
    idd = instance.product.id
    slug = slugify(title)
    signer123 = Signer()
    value = signer123.sign('')
    file_extension = filename.split(".")[1]
    new_filename = "%s-%s-%s.%s" % (slug, idd,  value, file_extension)
    return "products/%s/%s/featured/%s" % (slug, idd, new_filename)


class ProductFeatured(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_to_featured)
    upload_to_jumbotron = models.BooleanField(default=False)
    title = models.CharField(max_length=120, null=True, blank=True)
    text = models.CharField(max_length=220, null=True, blank=True)
    text_right = models.BooleanField(default=False)
    text_css_color = models.CharField(max_length=6, null=True, blank=True)
    show_price = models.BooleanField(default=False)
    make_image_background = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.product.title
