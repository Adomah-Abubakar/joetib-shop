from django.shortcuts import get_object_or_404, render, redirect
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.contrib import messages
from django.views.generic import ListView, DetailView
from . import models
from . import forms
# Create your views here.


def create_update_product(request: HttpRequest, pk:int=None):
    product = None
    if pk:
        product = get_object_or_404(models.Product, pk=pk)
    if request.method == "POST":
        product_form = forms.ProductForm(request.POST, files=request.FILES, instance=product )
        if product_form.is_valid():
            product: models.Product = product_form.save()
            messages.success(request, "Product {product.name} saved successfully")
            return redirect(product.get_update_url())
        else:
            messages.error(request, "Please fix the problems in the form.")
    else:
        product_form = forms.ProductForm(instance=product)
    return render(request, 'store/create_update_product.html', {'product_form': product_form })

def create_update_stock(request: HttpRequest, supply_pk: int, pk:int=None):
    stock: models.Stock =None
    supply: models.Supply = get_object_or_404(models.Supply, pk=supply_pk)
    if pk:
        stock = get_object_or_404(models.Stock, pk=pk)
    if request.method == "POST":
        stock_form = forms.StockForm(request.POST, files=request.FILES, instance=stock )
        if stock_form.is_valid():
            stock: models.Stock = stock_form.save(commit=False)
            stock.supply = supply
            stock.save()
            messages.success(request, f"Stock for {stock.product.name} saved successfully")
            messages.success(request, f"Redirecting to {supply.get_absolute_url()}")
            redirect(supply.get_absolute_url())
        else:
            messages.error(request, "Please fix the problems in the form.")
    else:
        stock_form = forms.StockForm(instance=stock)
    return render(request, 'store/create_update_stock.html', {'stock_form': stock_form })


class ProductListView(ListView):
    model = models.Product
    context_object_name = "products"
    template_name = "store/products_list.html"

class SupplyDetail(DetailView):
    model = models.Supply
    context_object_name = "supply"
    template_name = "store/supply_detail.html"

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['stock_form'] = forms.StockForm()
        return context

class SupplyListView(ListView):
    model = models.Supply
    context_object_name = "supplies"
    template_name = "store/supply_list.html"

def create_supply(request: HttpRequest):
    supply = models.Supply.objects.create()
    return redirect(supply.get_absolute_url())

def add_product_to_order(request: HttpRequest, pk:int) -> HttpResponse:
    order = models.Order.objects.get_or_create(completed=False)[0]
    product = get_object_or_404(models.Product, pk=pk)
    OrderItem = models.OrderItem.objects.get_or_create(order=order, product=product)