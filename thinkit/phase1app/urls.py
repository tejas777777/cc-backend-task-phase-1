from django.urls import path

from . import views

urlpatterns = [
    path('wallets/', views.WalletListCreateView.as_view(), name='wallet-list-create'),
    path('wallets/<int:pk>/', views.WalletDetailView.as_view(), name='wallet-detail'),

    path('items/', views.ItemListCreateView.as_view(), name='item-list-create'),
    path('items/<int:pk>/', views.ItemDetailView.as_view(), name='item-detail'),

    path('cart/', views.CartView.as_view(), name='cart-detail'),
    path('cart/items/', views.CartItemListCreateView.as_view(), name='cart-item-add'),
    path('cart/items/<int:item_id>/', views.CartItemDetailView.as_view(), name='cart-item-detail'),
]
