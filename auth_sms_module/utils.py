# sms/utils.py
import requests
import json
from django.conf import settings
import random
import string


def generate_verification_code(length=6):
    return ''.join(random.choices(string.digits, k=length))


def send_sms(recipient, verification_code):
    url = "https://api2.ippanel.com/api/v1/sms/pattern/normal/send"
    payload = json.dumps({
        "code": "cce5tnvle6hci76",  # Replace with your actual pattern code
        "sender": "+983000505",
        "recipient": recipient,
        "variable": {
            "verification-code": verification_code
        }
    })
    headers = {
        'apikey': settings.FARAZ_SMS_API_KEY,  # Store your API key in settings
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()


