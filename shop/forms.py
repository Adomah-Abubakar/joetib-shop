from django import forms

from django.db import models
from store.models import Order

class PaymentChoiceForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("payment_method",)

    