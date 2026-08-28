from rest_framework import serializers

from .models import Cart, CartItem, Item, Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'username', 'balance', 'currency', 'last_updated']
        read_only_fields = ['id', 'last_updated']


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = [
            'id', 'name', 'description', 'price', 'category',
            'stock', 'unit', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CartItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'item', 'quantity', 'subtotal']
        read_only_fields = ['id', 'item', 'subtotal']

    def get_subtotal(self, obj):
        return obj.quantity * obj.item.price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'created_at', 'updated_at']
        read_only_fields = fields

    def get_total_price(self, obj):
        return sum(cart_item.quantity * cart_item.item.price for cart_item in obj.items.all())
