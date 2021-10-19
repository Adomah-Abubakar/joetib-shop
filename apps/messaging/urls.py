from django.urls import path
from . import views

app_name = "messaging"

urlpatterns = [
    path('', views.HomePage.as_view(), name="home"),
    path('sms-list/create/', views.create_sms, name="create-sms"),
    path('sms-list/', views.SmsListView.as_view(), name="sms-list"),
    path('sms-list/<int:pk>/', views.SmsDetailView.as_view(), name="sms-detail"),
    path('email/test/', views.send_email, name="send_email"),
]