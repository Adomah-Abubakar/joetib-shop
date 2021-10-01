from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price")
@admin.register(models.ProductImage) 
class ProductImageAdmin(admin.ModelAdmin):
    pass
@admin.register(models.Supply)
class SupplyAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Stock)
class StockAdmin(admin.ModelAdmin):
    
    list_display = ("product", "supply", "stock_quantity", "available_quantity", "is_available", "single_item_price", "starting_estimated_profit")


@admin.register(models.ProductPurchase)
class ProductPurchaseAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    pass

@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("id", "image", "category", "title")