from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'index.html')

def services(request):
    return render(request, 'services.html')

def about(request):
    return render(request, 'about.html')

def login(request):
    return render(request, 'login.html')

def booking(request):
    return render(request, 'booking.html')