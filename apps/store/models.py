import decimal
from django.db import models
from django.db.models.fields import related
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth import get_user_model
# Create your models here.

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self) -> str:
        return reverse('shop:product-list', kwargs={'category_pk': self.pk})
    
    def get_products_count(self) -> int:
        return self.products.count()

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2, max_digits=12)
    discount_price = models.DecimalField(decimal_places=2, max_digits=12, blank=True, null=True)
    image = models.ImageField(upload_to="product-images/")
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str: 
        return self.name
    def get_price (self)-> str:
        if self.discount_price:
            return self.discount_price
        return self.price
    
    def get_add_to_cart_url(self) -> str:
        return reverse('shop:add-product-to-cart', kwargs={'product_pk': self.pk})

    def get_absolute_url(self) -> str:
        return reverse("shop:product-detail", kwargs={'pk': self.pk})

    def get_update_url(self) -> str:
        return reverse('store:create-update-product', kwargs={'pk': self.pk})

class Supply(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ('-date_created',)
    
    def __str__(self) -> str:
        return f"Supply on {self.date_created}"
    def get_absolute_url(self) -> str:
        return reverse('store:supply-detail', kwargs={'pk': self.pk})

    def get_add_stock_url(self) -> str:
        return reverse('store:create-update-stock', kwargs={'supply_pk': self.pk})
    
    def get_total_cost(self) -> Decimal:
        return sum([stock.get_total_cost() for stock in self.stocks.all()])
    
    def get_estimated_profit(self) -> Decimal:
        return sum([stock.get_estimated_profit() for stock in self.stocks.all()])
    
    def get_estimated_percentage_profit(self):
        result :Decimal = self.get_estimated_profit() * 100 / self.get_total_cost()
        return round(result, 2)
class Stock(models.Model):
    product: Product = models.ForeignKey(Product, related_name="stocks", on_delete=models.CASCADE)
    supply: Supply = models.ForeignKey(Supply, related_name="stocks", on_delete=models.CASCADE)
    stock_quantity = models.PositiveIntegerField(default=1)
    available_quantity = models.PositiveIntegerField(blank=True)
    single_item_price = models.DecimalField(decimal_places=2, max_digits=12)
    starting_estimated_profit = models.DecimalField(decimal_places=2, max_digits=12)
    is_available = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("date_created",)

    def __str__(self) -> str:
        return f"Stock of {self.product.name}"

    def get_total_cost(self) -> Decimal:
        return self.single_item_price * self.stock_quantity
    def get_update_url(self) -> str:
        return reverse('store:create-update-stock', kwargs={'supply_pk': self.supply.pk, 'pk': self.pk})
    
    def get_estimated_profit(self) -> Decimal:
        # TODO : Fix this to ensure that already sold items are computed.
        total_profit_made = Decimal(0)
        total_quantity_sold = 0
        # Check all already sold items and compute the profit made.
        for purchase in self.purchases.all():

            quantity= purchase.quantity
            profit_made = purchase.get_total_profit_made(), 
            total_profit_made += profit_made
            total_quantity_sold += total_quantity_sold
        return ((self.stock_quantity-total_quantity_sold) * self.product.get_price()) - self.get_total_cost()
    
    def is_profitable(self) -> bool:
        return self.get_estimated_profit() > 0

    def check_if_item_missing(self) -> tuple[bool, int]:
        """Checks if all items are accounted for in a stock."""
        quantity_sold = sum([purchase.quantity for purchase in self.purchases.all()])
        real_available_quantity =  self.stock_quantity - quantity_sold
        return real_available_quantity == self.available_quantity, real_available_quantity - self.available_quantity

    def save(self, *args, **kwargs):
        if self.available_quantity==None and self.stock_quantity:
            self.available_quantity = self.stock_quantity
        if not self.starting_estimated_profit:
            self.starting_estimated_profit = self.get_estimated_profit()
        super().save(*args, **kwargs)
    
    def deduct_quantity(self, quantity:int) -> int:
        if self.available_quantity >= quantity:
            remainder = 0
            self.available_quantity -= quantity
        else:
            remainder = quantity - self.available_quantity
            self.available_quantity = 0
        super().save()
        return remainder
    
class Address(models.Model):
    user = models.ForeignKey(User, related_name="addresses", blank=True, null=True, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=11)
    street_name = models.CharField(max_length=200)
    house_number = models.CharField(max_length=100, help_text="Use Ghana Post digital address if available.")
    extra_description = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-last_modified',)
    
    def __str__(self) -> str:
        return ', '.join([self.street_name, self.house_number])

class Order(models.Model):
    class PaymentChoices(models.TextChoices):
        cash = 'C'
        momo = "M"
    user = models.ForeignKey(User, related_name="orders", on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    address = models.ForeignKey(Address, related_name="orders", on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(choices=PaymentChoices.choices,default=PaymentChoices.cash, blank=True, max_length=2)
    is_completed=models.BooleanField(default=False)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order for {self.amount} on {self.date_created.day}"

    def get_absolute_url(self) -> str:
        return reverse("shop:order-detail", kwargs={'pk': self.pk})
    
    def place_order(self) -> bool:
        order_items = []
        for order_item in self.order_items.all():
            order_item.single_item_price = order_item.get_single_item_price()
            order_items.append(order_item)
        OrderItem.objects.bulk_update(order_items, fields=['single_item_price'])
        self.amount = sum([order_item.get_total_price() for order_item in order_items])
        self.ordered_date = timezone.now()
        self.ordered = True
        self.save()
    
    def get_number_of_items(self) -> int:
        return sum([order_item.quantity for order_item in self.order_items.all()])


class OrderItem(models.Model):
    order = models.ForeignKey(Order,  related_name="order_items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items",  on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    single_item_price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    def get_absolute_url(self) -> str:
        return reverse('shop:order-item-detail', kwargs={'order_id': self.order.id, 'pk': self.pk})
    def get_total_sold_price(self) -> Decimal:
        return self.quantity * self.get_single_item_price()
    
    def get_single_item_price(self):
        if self.single_item_price:
            return self.single_item_price
        return self.product.get_price()
    
    def get_total_price(self) -> Decimal:
        return self.get_single_item_price() * self.quantity
    
    def get_total_cost_price(self) -> Decimal:
        return self.stock.single_item_price * self.quantity
    
    def get_total_profit_made(self) -> Decimal:
        return self.get_total_sold_price() - self.get_total_cost_price()


class ProductPurchase(models.Model):
    product: Product = models.ForeignKey(Product, related_name="purchases", on_delete=models.CASCADE)
    stock: Stock = models.ForeignKey(Stock, related_name="purchases", on_delete=models.CASCADE)
    order_item = models.ForeignKey(OrderItem, related_name="product_purchases", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    single_item_price = models.DecimalField(decimal_places=2, max_digits=12)

    def get_total_sold_price(self) -> Decimal:
        return self.quantity * self.single_item_price
    
    def get_total_cost_price(self) -> Decimal:
        return self.stock.single_item_price * self.quantity
    
    def get_total_profit_made(self) -> Decimal:
        return self.get_total_sold_price() - self.get_total_cost_price()
