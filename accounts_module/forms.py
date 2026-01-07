from django import forms
from django.core import validators
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    mobile = forms.CharField(
        label='mobile',
        validators=[
            validators.MaxLengthValidator(100),
        ]
    )
    password = forms.CharField(
        label='کلمه عبور',
        widget=forms.PasswordInput(),
        validators=[
            validators.MaxLengthValidator(100),
        ]
    )

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if mobile and mobile.startswith('09') and len(mobile) == 11:
            return mobile

        raise ValidationError('شماره موبایل وارد شده معتبر نیست')

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password == confirm_password:
            return confirm_password

        raise ValidationError('کلمه عبور و تکرار آن مغایرت دارند')
