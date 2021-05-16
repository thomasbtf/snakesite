from django.urls import path
from django.contrib.auth.views import LoginView

from .views import profile_request, register_request, logout_request

app_name="users"

urlpatterns = [
    path('register/', register_request, name="register"),
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", logout_request, name= "logout"),
    path("profile/", profile_request, name= "profile"),
]
