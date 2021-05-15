from django.urls import path

from .views import register_request, login_request, logout_request

app_name="users"

urlpatterns = [
    path('register/', register_request, name="register"),
    path("login/", login_request, name="login"),
    path("logout/", logout_request, name= "logout"),
]
