from django.shortcuts import  render, redirect
from .forms import CustomUserForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages 
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

def register_request(request):
	if request.method == "POST":
		form = CustomUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful. You are now able to log in." )
			return redirect("user:login")
		messages.error(request, "Unsuccessful registration. Please check the provided information.")
	form = CustomUserForm
	return render (request=request, template_name="users/register.html", context={"register_form":form})


def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("workflow:index")

@login_required
def profile_request(request):
	return render(request, "users/profile.html")