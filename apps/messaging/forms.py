from crispy_forms.layout import Column, Layout, Row
from django import forms
from .models import Sms
from crispy_forms.helper import FormHelper

class SmsForm(forms.ModelForm):
    class Meta:
        model = Sms
        fields = ("message", "recipients", "other_recipients", "other_numbers", "is_draft")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            "message",
            Row(
                Column("recipients",),
                Column("other_recipients",),
            ),
            "other_numbers",
            "is_draft",
        )