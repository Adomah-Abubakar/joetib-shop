import requests
from django.conf import settings

class PayStack:
    PAYSTACK_PRIVATE_KEY = settings.PAYSTACK_PRIVATE_KEY
    PAYSTACK_PUBLIC_KEY = settings.PAYSTACK_PUBLIC_KEY
    base_url = 'https://api.paystack.co'


    def make_request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Helper function to make the appropriate request to paystack"""
        options = {
            "GET": requests.get,
            "POST": requests.post,
            "PUT": requests.put,
            "DELETE": requests.delete,
        }
        url = "{}{}".format(self.base_url, path)
        headers = {
            "Authorization": "Bearer {}".format(self.PAYSTACK_PRIVATE_KEY),
            "Content-Type": "application/json",
        }
        return options[method](url, headers=headers, **kwargs)

    def verify_payment(self, ref, amount:int):
        path = "/transaction/verify/{}".format(ref)
        response = self.make_request("GET", path)
        
        return self.verify_result(response)
    
    def check_balance(self):
        path = '/balance/'
        response = self.make_request("GET", path)
        return self.verify_result(response)
    
    def verify_result(self, response : requests.Response):
        if response.status_code == 200:
            response_data = response.json()
            return response_data['status'], response_data["data"]
        response_data = response.json()
        return response_data['status'], response_data['message']