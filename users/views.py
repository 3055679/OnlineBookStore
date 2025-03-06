# from django.shortcuts import redirect, render
# # from django.contrib.auth.forms import UserCreationForm
# from django.contrib import messages
# from django.contrib.auth import logout
# from .forms import RegisterForm

# def register(request):
#     if request.method == 'POST':
#         # form = UserCreationForm(request.POST)
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             user=form.save()
#             # username=form.cleaned_data.get('username')
            
#             messages.success(request,f'Welcome {user.username}, your account is created')
#             logout(request)  # Forcefully log out user to ensure they see the login page
#             print("Redirecting to:", redirect('login'))  # Debugging line
#             return redirect('login')
#     else:
#         form=RegisterForm()
#     return render(request, 'users/register.html',{'form':form})

from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Welcome {user.username}, your account has been created! Please log in.')

            logout(request)  # Ensure user is logged out
            request.session.pop('_messages', None)  # Clear all stored messages before redirect

            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


from django.contrib.messages import get_messages

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Clear any old messages before adding new ones
            storage = get_messages(request)
            for _ in storage:  
                pass  # This clears old messages from the session

            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('bookstore:home')  
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'users/login.html')


# Custom Logout View
def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return render(request, 'users/logout.html')


# def forgot_password(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         try:
#             user = User.objects.get(email=email)
#             token = default_token_generator.make_token(user)
#             uid = urlsafe_base64_encode(force_bytes(user.pk))

#             # Prepare the reset link email
#             reset_link = f"{get_current_site(request).domain}/reset-password/{uid}/{token}/"
#             subject = "Password Reset Request"
#             message = render_to_string('users/password_reset_email.html', {
#                 'user': user,
#                 'reset_link': reset_link,
#             })

#             # Send reset email
#             send_mail(subject, message, 'admin@bookstore.com', [email])

#             return redirect('password_reset_done')  # Create this template as a success message page
#         except User.DoesNotExist:
#             pass  # If email not found, we can either handle it or silently pass

#     return render(request, 'users/forgot_password.html')


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Find all users with the given email
        users = User.objects.filter(email=email)  # Use .filter() instead of .get()

        if not users.exists():
            messages.error(request, "No user found with this email. Please try again.")
            return redirect("forgot-password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match. Please try again.")
            return redirect("forgot-password")

        # Reset password for all accounts with the same email
        for user in users:
            user.set_password(new_password)  # Hashes and updates the password
            user.save()

        messages.success(request, "Your password has been reset. Please log in.")
        return redirect("login")  # Redirect to login page

    return render(request, "users/forgot_password.html")

# Reset password view
def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')

                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                    return redirect('login')  # Redirect to login page after successful reset

            return render(request, 'users/reset_password.html')

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return redirect('password_reset_invalid')  # Create an invalid link template
    

def password_reset_done(request):
    return render(request, 'users/password_reset_done.html')


def password_reset_invalid(request):
    return render(request, 'users/password_reset_invalid.html')


