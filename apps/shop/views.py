import re

from django.contrib.auth import login
from apps.shop.forms import PaymentChoiceForm
from django.db.models import query
from django.shortcuts import get_object_or_404, render, redirect
from django.http.response import HttpResponse, JsonResponse
from django.http.request import HttpRequest
from django.views.generic import ListView, DetailView, View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

# Create your views here.
from apps.store.models import Banner, Payment, Product, Category, Order, OrderItem, Address
from apps.store.forms import AddressForm

from . import cookie_store


class HomePage(ListView):
    model = Category
    context_object_name = "categories"
    template_name = "shop/homepage.html"
    def get_queryset(self):
        return Category.objects.all()[:7]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context["banners"] = Banner.objects.filter(category=None)[:5]
        context["all_products_count"] = Product.objects.all().count()

        return context


class ProductListView(ListView):
    model = Product
    paginate_by = 12
    context_object_name = "products"
    template_name = "shop/shop.html"
    current_category = None
    search_query = None

    def get_queryset(self, *args, **kwargs):
        category_pk = self.kwargs.get("category_pk")
        queryset = super().get_queryset()
        self.search_query = self.request.GET.get("search", None)
        if self.search_query:
            queryset = queryset.filter(name__icontains=self.search_query)
        if category_pk:
            self.current_category = get_object_or_404(Category, pk=category_pk)
            queryset = queryset.filter(category=self.current_category)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["categories"] = Category.objects.all()
        context["current_category"] = self.current_category
        context["all_products_count"] = Product.objects.all().count()
        context["search_query"] = self.search_query
        return context


class ProductDetailView(DetailView):
    model = Product
    context_object_name = "product"
    template_name = "shop/product.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cookie_store.RecentList(self.request).add(self.get_object())
        return context


@login_required
def add_product_to_order(request: HttpRequest, product_pk: int) -> HttpResponse:

    order: Order = Order.objects.get_or_create(ordered=False, user=request.user)[0]
    quantity: int = int(request.GET.get("quantity", 1))
    product: Product = get_object_or_404(Product, pk=product_pk)
    order_item_qs = OrderItem.objects.filter(order=order, product=product)
    if order_item_qs.exists():
        order_item: OrderItem = order_item_qs.first()
        order_item.quantity += quantity
        order_item.save()
    else:
        order_item: OrderItem = OrderItem.objects.create(
            order=order, product=product, quantity=quantity
        )
    messages.success(request, f"Product '{product.name}' has been added to cart.")
    return redirect("shop:cart")

@login_required
def add_product_to_cart_json(request: HttpRequest, product_pk: int):
    quantity = int(request.GET.get("quantity", 1))
    order = Order.objects.get_or_create(ordered=False, user=request.user)[0]
    product = get_object_or_404(Product, pk=product_pk)
    order_item_qs = OrderItem.objects.filter(order=order, product=product)
    if order_item_qs.exists():
        order_item: OrderItem = order_item_qs.first()
        order_item.quantity += quantity
        if order_item.quantity == 0:
            order_item.delete()
        else:
            order_item.save()

    else:
        order_item: OrderItem = OrderItem.objects.create(
            order=order, product=product, quantity=quantity
        )
    return JsonResponse(
        {"quantity": order_item.quantity, "total": order_item.get_total_price()}
    )


@login_required
def cart_view(request: HttpRequest):
    order, _ = Order.objects.get_or_create(ordered=False, user=request.user)
    return render(request, "shop/cart.html", {"order": order})


class CheckOut(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs):
        if self.kwargs.get("address_pk"):
            return self.post(request, *args, **kwargs)
        order, _ = Order.objects.get_or_create(ordered=False, user=request.user)
        if order.order_items.count() < 1:
            messages.error(request, "Sorry you do not have any items in your order.")
            return redirect("shop:product-list")
        address_form = AddressForm()
        return render(
            request,
            "shop/checkout.html",
            {"address_form": address_form, "order": order},
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        order, _ = Order.objects.get_or_create(ordered=False, user=request.user)
        if order.order_items.count() < 1:
            messages.error(request, "Sorry you do not have any items in your order.")
            return redirect("shop:product-list")
        if self.kwargs.get("address_pk"):
            address_qs = Address.objects.filter(
                user=request.user, pk=int(self.kwargs.get("address_pk"))
            )
            if address_qs.exists():
                address = address_qs.first()
            else:
                messages.error(request, "The given address was not found.")
                return self.get(self, request, *args, **kwargs)
        else:
            address_form = AddressForm(request.POST)
            if address_form.is_valid():
                address = address_form.save(commit=False)
                address.user = request.user
                address.save()
        order.address = address
        order.save()
        self.kwargs["address_pk"] = None
        messages.success(request, "Address saved.")
        return redirect("shop:payment-choice")


class PaymentChoice(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        order, _ = Order.objects.get_or_create(ordered=False, user=request.user)
        if order.order_items.count() < 1:
            messages.error(request, "Sorry you do not have any items in your order.")
            return redirect("shop:product-list")
        payment_choice_form = PaymentChoiceForm()
        return render(
            request,
            "shop/payment_choices.html",
            {"payment_choice_form": payment_choice_form, "order": order},
        )

    def post(self, request, *args, **kwargs):
        order: Order
        order, _ = Order.objects.get_or_create(ordered=False, user=request.user)
        if order.order_items.count() < 1:
            messages.error(request, "Sorry you do not have any items in your order.")
            return redirect("shop:product-list")
        payment_choice_form = PaymentChoiceForm(request.POST, instance=order)
        if payment_choice_form.is_valid():
            order = payment_choice_form.save()
        if order.payment_method == Order.PaymentChoices.cash:
            order.place_order()
            messages.success(request, "Your Order has been recorded.")
            return redirect("shop:cart")
        else:
            return redirect(order.get_payment_url())


class MomoPayment(LoginRequiredMixin, View):
    def get(self, request, pk=None, *args, **kwargs):
        order: Order
        if pk:
            order = get_object_or_404(Order, user=request.user, pk=pk)
        else:
            order = get_object_or_404(Order, ordered=False, user=request.user)
        if not order.address:
            messages.error(request, "Cannot process order for payment without address.")
            return redirect("shop:product-list")

        if order.order_items.count() < 1:
            messages.error(request, "Sorry you do not have any items in your order.")
            return redirect("shop:product-list")
        payment_qs = order.payments.filter(paid=False, payment_type=Payment.PaymentChoices.momo)
        if order.compute_amount_to_pay() <= 0:
            return redirect(order.get_absolute_url())
        if payment_qs.exists():
            payment = payment_qs.first()
            payment.amount = order.compute_amount_to_pay()
        else:
            payment = Payment.objects.create(
                order=order,
                amount=order.compute_amount_to_pay(),
                payment_type=Payment.PaymentChoices.momo,
            )
        return render(request, "shop/make_payment.html", {'payment': payment, 'order': order, "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY})
    
    
class ConfirmMomoPayment(LoginRequiredMixin, DetailView):
    model = Payment

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        payment: Payment = self.get_object()
        confirmed, message = payment.confirm_payment()
        if confirmed:
            messages.success(request, message)
            payment.order.place_order()
            return redirect(payment.order.get_absolute_url())
        else:
            messages.error(request, message)
        return redirect(payment.order.get_payment_url())
class OrderList(LoginRequiredMixin, ListView):
    model = Order
    context_object_name = "orders"
    paginate_by = 12
    template_name = "shop/order_list.html"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, ordered=True).order_by(
            "is_completed"
        )


class OrderDetail(LoginRequiredMixin, DetailView):
    model = Order
    context_object_name = "order"
    template_name = "shop/order_detail.html"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, ordered=True)


class OrderItemDetail(LoginRequiredMixin,DetailView):
    model = OrderItem
    context_object_name = "order_item"
    template_name = "shop/order_item_detail.html"

    def get_queryset(self):
        return OrderItem.objects.filter(
            order__user=self.request.user, order__ordered=True
        )
