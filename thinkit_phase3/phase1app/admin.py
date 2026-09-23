from django.contrib import admin

from .models import Cart, CartItem, Item, Order, OrderItem, Profile, Review, Wallet

admin.site.register(Profile)
admin.site.register(Wallet)
admin.site.register(Item)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)
