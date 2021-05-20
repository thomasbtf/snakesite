from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    avatar_image_request,
    logout_request,
    profile_request,
    register_request,
    rnd_avatar_request,
)

app_name = "users"

urlpatterns = [
    path("register/", register_request, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path("logout/", logout_request, name="logout"),
    path("profile/", profile_request, name="profile"),
    path("random-avatar/", rnd_avatar_request, name="avatar"),
    path("avatar.<seed>.png", avatar_image_request, name="avatar-rnd"),
]
