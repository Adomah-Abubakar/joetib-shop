from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
from django.urls import reverse
from django.conf import settings
from .sms import SmsApi

User = get_user_model()

class Contact(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name
    
class Sms(models.Model):
    message = models.TextField()
    recipients = models.ManyToManyField(User, related_name="received_sms", blank=True)
    other_recipients = models.ManyToManyField(Contact, blank=True, null=True, related_name="received_sms")
    other_numbers  = models.TextField(blank=True, help_text="Enter phone numbers seperated by commas (,)")
    is_draft = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-last_modified",)

    def __str__(self):
        return self.message

    
    def get_absolute_url(self):
        return reverse("messaging:sms-detail", kwargs={'pk': self.pk})
    
    def get_other_numbers_list(self):
        return [number.strip() for number in self.other_numbers.split(',')] 
    
    def get_recipients_count(self):
        if not self.other_numbers:
            return self.recipients.count()
        return self.recipients.count() + len(self.other_numbers.split())

    def send_sms(self, *args, **kwargs):
        # TODO: fix send
        if self.sent:
            print("Sms already sent")
            return True

        recipients= [user.phone_number for user in self.recipients.all()]
        recipients += [contact.phone_number for contact in self.other_recipients.all()]

        if self.other_numbers:
            recipients += self.get_other_numbers_list()
        sent = SmsApi().send(recipients=recipients, message=self.message, sender_id=settings.SMS_SENDER_ID)
        if sent:
            self.sent = sent
            self.save()
        return sent
        
    