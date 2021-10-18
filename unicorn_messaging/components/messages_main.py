from django_unicorn.views import UnicornView
from apps.messaging.models import Sms
class MessagesMainView(UnicornView):
    model = Sms
    messages = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.messages = Sms.objects.all()
    
    

