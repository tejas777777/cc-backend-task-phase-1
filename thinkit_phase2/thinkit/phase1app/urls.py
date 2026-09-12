from django.urls import path

from . import views

urlpatterns = [
    path('auth/signup/', views.SignupView.as_view(), name='signup'),
    path('auth/me/', views.MeView.as_view(), name='me'),

    path('wallet/', views.WalletView.as_view(), name='wallet-detail'),
    path('wallet/topup/', views.WalletTopUpView.as_view(), name='wallet-topup'),

    path('items/', views.ItemListCreateView.as_view(), name='item-list-create'),
    path('items/<int:pk>/', views.ItemDetailView.as_view(), name='item-detail'),
    path('items/<int:item_id>/reviews/', views.ItemReviewListCreateView.as_view(), name='item-reviews'),

    path('cart/', views.CartView.as_view(), name='cart-detail'),
    path('cart/items/', views.CartItemListCreateView.as_view(), name='cart-item-add'),
    path('cart/items/<int:item_id>/', views.CartItemDetailView.as_view(), name='cart-item-detail'),

    path('checkout/', views.CheckoutView.as_view(), name='checkout'),

    path('seller/items/', views.SellerItemListView.as_view(), name='seller-items'),
    path('seller/orders/', views.SellerOrderListView.as_view(), name='seller-orders'),
]
