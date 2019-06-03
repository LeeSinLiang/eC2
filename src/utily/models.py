from decimal import Decimal
from django.db import models
from django.conf import settings
from django.urls import reverse
from products.models import Product
from orders.models import UserCheckout
from django.shortcuts import redirect

# Create your models here.


class Review(models.Model):
    user                = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)
    product             = models.ForeignKey(Product, on_delete=models.CASCADE)
    ratings             = models.DecimalField(default=0, max_digits=5, decimal_places=1)
    verified_purchase   = models.BooleanField(default=False)
    content             = models.TextField()
    timestamp           = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.username)

    @property
    def average_ratings(self):
        allratings = Review.objects.all()
        average = 0
        for ar in allratings:
            average += ar.ratings
        print('line')
        print(average)
        average = Decimal(average/allratings.count())
        return average
    # def get_absolute_url(self):
    #     return reverse("comments", kwargs={"id": self.id})

    # def get_delete_url(self):
    #     return reverse("comments:delete", kwargs={"id": self.id})

class Wishlist(models.Model):
    user                = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)
    product             = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.product.title

    def delete_object(self):
        return "%s?item=%s&delete=True" % (reverse("wishlist"), self.product.id)
        # return redirect("wishlist")

class History(models.Model):
    user                = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)
    product             = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + '-' + self.product.title