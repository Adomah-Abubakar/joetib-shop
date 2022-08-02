from django.urls import path
from . import views
app_name = "store"


urlpatterns = [
    path('products/', views.ProductListView.as_view(), name="product-list"),
    path('products/create/', views.create_update_product, name="create-update-product"),
    path('products/update/<int:pk>/', views.create_update_product, name="create-update-product"),
    path('supply/create/', views.create_supply, name="create-supply"),
    path('supply/', views.SupplyListView.as_view(), name="supply-list"),
    path('supply/<int:pk>/', views.SupplyDetail.as_view(), name="supply-detail"),
    path('supply/<int:supply_pk>/stock/create/', views.create_update_stock, name="create-update-stock"),
    path('supply/<int:supply_pk>/stock/update/<int:pk>/', views.create_update_stock, name="create-update-stock"),

]