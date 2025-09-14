# forms.py
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "phone", "address")

    def save(self, commit=True):
        user = super().save(commit=False)  # จะได้ username + (password จะ set โดย UserCreationForm)
        # กำหนดฟิลด์เสริมให้ชัดเจน
        user.email = self.cleaned_data.get("email", "")
        user.phone = self.cleaned_data.get("phone", "")
        user.address = self.cleaned_data.get("address", "")
        if commit:
            user.save()
        return user
    
class LoginForm(forms.Form):
    identifier = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={"placeholder": "Username or Email"})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )
    remember = forms.BooleanField(
        label="จดจำฉัน", required=False
    )

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Email"})
    )
    address = forms.CharField(
        label="Address", required=False,
        widget=forms.TextInput(attrs={"placeholder": "Address"})
    )
    phone = forms.CharField(
        label="Phone", required=False,
        widget=forms.TextInput(attrs={"placeholder": "Phone"})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "email", "password1", "password2", "address", "phone"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("อีเมลนี้ถูกใช้ไปแล้ว")
        return email
