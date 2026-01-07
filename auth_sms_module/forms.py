from django import forms
from django.core import validators
from django.core.exceptions import ValidationError

class VerificationSmsForm(forms.Form):
    sms_code = forms.CharField(
        max_length=6,
        required=False,
        label='کد احراز هویت',
    )