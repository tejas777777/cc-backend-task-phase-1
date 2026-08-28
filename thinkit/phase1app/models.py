from django.conf import settings
from django.db import models


class Wallet(models.Model):
    username = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=10, decimal_places=0)
    currency = models.CharField(max_length=3, default='INR')
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    stock = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=20, default='pieces')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart({self.user.username})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'item')

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"
