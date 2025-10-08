from allauth.account.forms import LoginForm
from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class CustomLoginForm(LoginForm):
    remember_me = forms.BooleanField(
        required=False, initial=True, label="Remember Me"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Email or Username'}
        )
        self.fields['password'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password'}
        )
        self.fields['remember_me'].widget = forms.CheckboxInput(
            attrs={'class': 'form-check-input'}
        )


class CustomSignupForm(SignupForm):
    """Custom signup form that only uses email + password + confirm password"""

    def save(self, request):
        # Call the base class save to create the user
        user = super().save(request)
        # You can customize user fields here if needed in the future
        user.save()
        return user


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2"]


class LoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
