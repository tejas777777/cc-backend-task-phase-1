from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Cart, CartItem, Item, Order, OrderItem, Profile, Review, Wallet


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=Profile.Role.choices)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already taken.')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['username'], password=validated_data['password'])
        Profile.objects.create(user=user, role=validated_data['role'])
        Wallet.objects.create(user=user)
        Cart.objects.create(user=user)
        return user


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'balance', 'currency', 'created_at', 'updated_at']
        read_only_fields = fields


class WalletTopUpSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))


class ItemSerializer(serializers.ModelSerializer):
    seller = serializers.ReadOnlyField(source='seller.username')
    average_rating = serializers.FloatField(read_only=True, allow_null=True)

    class Meta:
        model = Item
        fields = [
            'id', 'name', 'description', 'price', 'category', 'stock', 'unit',
            'seller', 'average_rating', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'seller', 'average_rating', 'created_at', 'updated_at']


class SellerItemSerializer(ItemSerializer):
    low_stock = serializers.SerializerMethodField()

    class Meta(ItemSerializer.Meta):
        fields = ItemSerializer.Meta.fields + ['low_stock']

    def get_low_stock(self, obj):
        return obj.stock < 5


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


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Review
        fields = ['id', 'user', 'item', 'rating', 'review_text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'item', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError('rating must be between 1 and 5.')
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'item', 'item_name', 'quantity', 'price_at_purchase']
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'total_price', 'status', 'created_at', 'items']
        read_only_fields = fields


class SellerOrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    buyer = serializers.ReadOnlyField(source='order.user.username')
    order_status = serializers.ReadOnlyField(source='order.status')
    ordered_at = serializers.ReadOnlyField(source='order.created_at')

    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'item', 'item_name', 'buyer',
            'quantity', 'price_at_purchase', 'order_status', 'ordered_at',
        ]
        read_only_fields = fields
