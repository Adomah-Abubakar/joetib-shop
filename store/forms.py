from . import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit, Row, Column

from django import forms


class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = ("name", "price", "category", "image", "description")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "name",
            "price",
            "category",
            "image",
            "description",
        )
        self.helper.form_tag = False


class StockForm(forms.ModelForm):
    class Meta:
        model = models.Stock
        fields = (
            "product",
            "single_item_price",
            "stock_quantity",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "product",
            "single_item_price",
            "stock_quantity",
        )
        self.helper.form_tag = False

class AddressForm(forms.ModelForm):
    class Meta:
        model = models.Address
        fields = ("phone_number", "street_name", "house_number", "extra_description" )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "phone_number",
            "street_name",
            "house_number",
            "extra_description",
        )
        self.helper.form_tag = False