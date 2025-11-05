from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Acest nume de utilizator există deja.')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)

        # Dacă ai câmpuri personalizate în modelul User (is_participant, is_organizer)
        if hasattr(user, 'is_participant') and role == 'participant':
            user.is_participant = True
        elif hasattr(user, 'is_organizer') and role == 'organizer':
            user.is_organizer = True

        user.save()
        messages.success(request, 'Cont creat cu succes! Te poți conecta acum.')
        return redirect('login')

    return render(request, 'users/register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Date de autentificare incorecte.')

    return render(request, 'users/login.html')


@login_required(login_url='login')
def profile(request):
    return render(request, 'users/profile.html', {'user': request.user})


@login_required(login_url='login')
def user_logout(request):
    logout(request)
    messages.info(request, 'Te-ai deconectat cu succes.')
    return redirect('login')
