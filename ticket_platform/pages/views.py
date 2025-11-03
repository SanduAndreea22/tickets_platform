from django.shortcuts import render, redirect
from .models import ContactMessage

def about(request):
    return render(request, 'pages/about.html')



