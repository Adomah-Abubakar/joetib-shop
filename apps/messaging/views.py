from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.contrib import messages
from apps.messaging.models import Sms
from .forms import SmsForm


# Create your views here.

class HomePage(TemplateView):
    template_name = "messaging/homepage.html"


class SmsListView(ListView):
    model = Sms
    paginate_by = 24
    context_object_name = "sms_messages"
    template_name = "messaging/sms_list.html"

class SmsDetailView(DetailView):
    model = Sms
    context_object_name = "sms_message"
    template_name = "messaging/sms_detail.html"

def create_sms(request: HttpRequest ) -> HttpResponse:
    if request.method == "POST":
        sms_form = SmsForm(request.POST)
        if sms_form.is_valid():
            sms: Sms = sms_form.save()
            if not sms.is_draft:
                sent = sms.send_sms()
                if sent:
                    messages.success(request, "Sms sent successfully")
                else:
                    messages.error(request, "Sorry, could not send sms")
            else:
                messages.success(request, "Sms has been saved as draft.")
    else:
        sms_form = SmsForm()
    return render(request, "messaging/create_sms.html", {'sms_form': sms_form})
