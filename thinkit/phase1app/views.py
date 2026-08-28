from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from phase1app.models import Cart, CartItem, Item, Wallet
from phase1app.serializers import CartItemSerializer, CartSerializer, ItemSerializer, WalletSerializer


class WalletListCreateView(generics.ListCreateAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class WalletDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class ItemListCreateView(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


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
    """View the current user's cart (with computed total) or clear it."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)

    def delete(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemListCreateView(APIView):
    """Add an item to the current user's cart."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

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
    """Update the quantity of, or remove, a single item already in the current user's cart."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

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
