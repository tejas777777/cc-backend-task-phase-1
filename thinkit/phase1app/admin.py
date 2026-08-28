from django.contrib import admin

from .models import Cart, CartItem, Item, Wallet

admin.site.register(Wallet)
admin.site.register(Item)
admin.site.register(Cart)
admin.site.register(CartItem)
