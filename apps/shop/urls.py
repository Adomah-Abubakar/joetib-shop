from django.urls import path

from . import views
app_name = "shop"

urlpatterns = [
    path('', views.HomePage.as_view(), name="home-page"),
    path('shop/', views.ProductListView.as_view(), name="product-list"),
    path('shop/<int:category_pk>/', views.ProductListView.as_view(), name="product-list"),
    path('shop/products/<int:pk>/', views.ProductDetailView.as_view(), name="product-detail"),
    path('cart/', views.cart_view, name="cart"),
    path('cart/add/<int:product_pk>/', views.add_product_to_order, name="add-product-to-cart"),
    path('cart/add/<int:product_pk>/json/', views.add_product_to_cart_json, name="add-product-to-cart-json"),
    path('checkout/', views.CheckOut.as_view(), name="checkout"),
    path('checkout/<int:address_pk>/', views.CheckOut.as_view(), name="checkout"),
    path('payment/', views.PaymentChoice.as_view(), name="payment-choice"),
    path('orders/', views.OrderList.as_view(), name="order-list"),
]
