import re

from django.contrib.auth import login
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.forms.models import ModelForm

from root.models import User


class RegisterForm(ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'phone_number', 'password']

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        phone_number = re.sub(r'\D', "", phone_number)
        if User.objects.filter(phone_number=phone_number).first():
            raise ValidationError("Ushbu telefon raqam allaqachon mavjud")

        return phone_number

    def clean_password(self):
        password = self.cleaned_data['password']
        password = make_password(password)
        return password


class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['phone_number', 'password']

    def __init__(self, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(**kwargs)

    def clean(self):
        phone_number = self.cleaned_data['phone_number']
        phone_number = re.sub(r'\D', "", phone_number)
        password = self.cleaned_data['password']
        user_data = User.objects.filter(phone_number=phone_number).first()

        if not user_data:
            raise ValidationError("Bundey raqam topilmadi")
        if not check_password(password, user_data.password):
            raise ValidationError("Parol xato kiritildi")
        login(self.request, user_data)
