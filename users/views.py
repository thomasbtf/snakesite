import io
import os
import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.cache import add_never_cache_headers, patch_cache_control

from .forms import ProfileCreateForm, ProfileUpdateForm, UserUpdateForm
from .models import Profile
from .utils import create_avatar_image, generate_avatar


def register_request(request):
    if request.method == "POST":
        form = ProfileCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, "Registration successful. You are now able to log in."
            )
            return redirect("user:login")
        messages.error(
            request, "Unsuccessful registration. Please check the provided information."
        )
    form = ProfileCreateForm
    return render(
        request=request,
        template_name="users/register.html",
        context={"register_form": form},
    )


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("workflow:index")


@login_required
def profile_request(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile hast been updated!")
            return redirect("user:profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {"u_form": u_form, "p_form": p_form}

    return render(request, "users/profile.html", context)


def rnd_avatar_request(request):
    if request.method == "POST":
        seed = request.POST.get("seed")
        instance = Profile.objects.get(id=request.user.profile.pk)
        abs_img = "".join([os.path.join(settings.AVATARS, str(seed)), ".svg"])
        rel_img = "".join(
            [os.path.join(os.path.basename(settings.AVATARS), str(seed)), ".svg"]
        )
        create_avatar_image(abs_img, seed=seed)
        instance.image = rel_img
        instance.save()
        # messages.success(request, "Your avatar hast been updated!" )
        return redirect("user:profile")

    context = {"rnd_seed": random.randint(1, 100000)}

    return render(request, "users/avatar.html", context)


def avatar_image_request(request, seed=None):
    bytes = io.BytesIO()
    avatar = generate_avatar(seed)
    avatar.render_png_file(bytes)
    response = HttpResponse(bytes.getvalue())
    response["content-type"] = "image/png"
    if seed == "random":
        add_never_cache_headers(response)
    else:
        patch_cache_control(response, max_age=60, public=True)

    return response
