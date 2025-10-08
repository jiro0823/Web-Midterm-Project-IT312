# accounts/urls.py
from django.urls import path, include
from .views import CustomLoginView
from .views import CustomSignupView
from accounts import views as accounts_views
from .views import custom_logout_view
from accounts import views


urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="account_login"),
    path("signup/", CustomSignupView.as_view(), name="account_signup"),
    path("signout/", custom_logout_view, name="custom_logout"),
    path('accounts/', include('allauth.urls')),

    path("dashboard/", accounts_views.dashboard, name="dashboard"),
    path("", accounts_views.home, name="home"),

    path('security-auth/', views.security_auth_panel, name='security_auth'),
    path('cipher-panel/', views.cipher_panel, name='cipher_panel'),

    path("cipher/", views.cipher_encryption, name="cipher"),
    path('Qr/', views.QR_view, name='Qr'),
    path('api-panel/', views.api_integration_panel, name='api_panel'),
    path('automation-panel/', views.automation_panel, name='automation_panel'),

    path('jokeapi/', views.jokeapi_encrypt_qr_panel, name='joke_api'),


    path('automation/', views.automation_panel, name='automation'),

    path('panel6/', views.panel6_page, name='panel6'),
]
