from django.shortcuts import render, redirect
from .models import SupportMessage

def contact(request):
    messages = SupportMessage.objects.all().order_by('-created_at')

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        SupportMessage.objects.create(
            name=name,
            email=email,
            message=message
        )
        return redirect('contact')

    return render(request, 'pages/contact.html', {'messages': messages})

def about(request):
    return render(request, 'pages/about.html')

def terms(request):
    return render(request, 'pages/terms.html')

def privacy(request):
    return render(request, 'pages/privacy.html')

def partners(request):
    return render(request, 'pages/partners.html')

def home(request):
    return render(request, 'pages/home.html')



