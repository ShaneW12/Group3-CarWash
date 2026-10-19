from django.shortcuts import render, redirect
from .Customer import Customer

def signup(request):

        if request.method == "POST":
            customer = Customer(
            request.POST["first_name"],
            request.POST["last_name"],
            request.POST["email"],
            request.POST["phone"]
            )

        

            return redirect("home")

        return render(request, "signup.html")
# Create your views here.
