from django.db import transaction
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from phase1app.filters import ItemFilterSet
from phase1app.models import Cart, CartItem, Item, Order, OrderItem, Review, Wallet
from phase1app.permissions import IsBuyer, IsItemOwner, IsSeller
from phase1app.serializers import (
    CartItemSerializer, CartSerializer, ItemSerializer, OrderSerializer,
    ReviewSerializer, SellerItemSerializer, SellerOrderItemSerializer,
    SignupSerializer, WalletSerializer, WalletTopUpSerializer,
)



class SignupView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'id': user.id, 'username': user.username, 'role': user.profile.role},
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'id': request.user.id,
            'username': request.user.username,
            'role': getattr(getattr(request.user, 'profile', None), 'role', None),
        })


class WalletView(APIView):
    """View the current buyer's wallet balance."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsBuyer]

    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        return Response(WalletSerializer(wallet).data)


class WalletTopUpView(APIView):
    """Simulate crediting the current buyer's wallet."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsBuyer]

    def post(self, request):
        serializer = WalletTopUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        wallet.balance += serializer.validated_data['amount']
        wallet.save(update_fields=['balance'])
        return Response(WalletSerializer(wallet).data)


class ItemListCreateView(generics.ListCreateAPIView):
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ItemFilterSet
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'average_rating', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Item.objects.annotate(average_rating=Avg('reviews__rating'))

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsSeller()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Item.objects.annotate(average_rating=Avg('reviews__rating'))

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAuthenticated(), IsSeller(), IsItemOwner()]
        return [IsAuthenticated()]


class ItemReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Review.objects.filter(item_id=self.kwargs['item_id']).order_by('-created_at')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsBuyer()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        item = get_object_or_404(Item, pk=self.kwargs['item_id'])
        if not OrderItem.objects.filter(order__user=request.user, item=item).exists():
            return Response(
                {'detail': 'You can only review items you have purchased.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Upsert: a second rating from the same user edits their existing review instead of erroring.
        existing = Review.objects.filter(user=request.user, item=item).first()
        serializer = self.get_serializer(existing, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, item=item)
        return Response(serializer.data, status=status.HTTP_200_OK if existing else status.HTTP_201_CREATED)


def _validate_quantity(raw_quantity, stock, item):
    try:
        quantity = int(raw_quantity)
    except (TypeError, ValueError):
        return None, Response({'detail': 'quantity must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
    if quantity < 1:
        return None, Response({'detail': 'quantity must be at least 1.'}, status=status.HTTP_400_BAD_REQUEST)
    if quantity > stock:
        return None, Response(
            {'detail': f"Only {stock} {item.unit} of '{item.name}' available in stock."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return quantity, None


class CartView(APIView):
    """View the current buyer's cart (with computed total) or clear it."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsBuyer]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)

    def delete(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemListCreateView(APIView):
    """Add an item to the current buyer's cart."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsBuyer]

    def post(self, request):
        item = get_object_or_404(Item, pk=request.data.get('item_id'))
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item, defaults={'quantity': 0})

        requested_quantity = request.data.get('quantity', 1)
        try:
            requested_quantity = int(requested_quantity)
        except (TypeError, ValueError):
            return Response({'detail': 'quantity must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        new_quantity, error = _validate_quantity(cart_item.quantity + requested_quantity, item.stock, item)
        if error:
            if created:
                cart_item.delete()
            return error

        cart_item.quantity = new_quantity
        cart_item.save()
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    """Update the quantity of, or remove, a single item already in the current buyer's cart."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsBuyer]

    def get_cart_item(self, request, item_id):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return get_object_or_404(CartItem, cart=cart, item_id=item_id)

    def patch(self, request, item_id):
        cart_item = self.get_cart_item(request, item_id)
        quantity, error = _validate_quantity(request.data.get('quantity'), cart_item.item.stock, cart_item.item)
        if error:
            return error
        cart_item.quantity = quantity
        cart_item.save()
        return Response(CartItemSerializer(cart_item).data)

    def delete(self, request, item_id):
        cart_item = self.get_cart_item(request, item_id)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CheckoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsBuyer]

    def post(self, request, *args, **kwargs):
        
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # lock the items in the cart at this stage to avoid race conditions
        cart_items = list(cart.items.select_related('item').select_for_update())

        if not cart_items:
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)
        
        insufficient_stock = [
            {'item_id': ci.item.id, 'name': ci.item.name, 'available': ci.item.stock, 'requested': ci.quantity}
            for ci in cart_items if ci.quantity > ci.item.stock
        ]
        if insufficient_stock:
            return Response(
                {'detail': 'Some items are out of stock.', 'items': insufficient_stock},
                status=status.HTTP_409_CONFLICT,
            )
	
        total_price = sum(ci.quantity * ci.item.price for ci in cart_items)
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        if wallet.balance < total_price:
            return Response(
                {'detail': 'Insufficient wallet balance.', 'balance': wallet.balance, 'required': total_price},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

            order = Order.objects.create(user=request.user, total_price=total_price)
            # the following operations are atomic, to maintain consistency
            with transaction.atomic():
                for ci in cart_items:
                    OrderItem.objects.create(
                    order=order, item=ci.item, seller_id=ci.item.seller_id,
                    quantity=ci.quantity, price_at_purchase=ci.item.price,
                )
                ci.item.stock -= ci.quantity
                ci.item.save(update_fields=['stock'])
                wallet.balance -= total_price
                wallet.save(update_fields=['balance'])
            cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class SellerItemListView(generics.ListAPIView):
    """Seller-only inventory dashboard: only the requesting seller's own items."""
    serializer_class = SellerItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSeller]

    def get_queryset(self):
        return Item.objects.filter(seller=self.request.user).annotate(average_rating=Avg('reviews__rating'))


class SellerOrderListView(generics.ListAPIView):
    """Seller-only view of order line items placed for their items."""
    serializer_class = SellerOrderItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSeller]

    def get_queryset(self):
        return (
            OrderItem.objects.filter(seller=self.request.user)
            .select_related('order', 'item', 'order__user')
            .order_by('-order__created_at')
        )

