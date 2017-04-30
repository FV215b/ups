from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from copy import deepcopy

# Create your views here.
def signup(request):
    if request.method == "POST":
        if request.POST["password1"] != request.POST["password2"]:
            return render(request, "accounts/signup.html", {"message": "please enter the same password"})
        else:
            try:
                User.objects.get(username = request.POST["username"])
                return render(request, "accounts/signup.html", {"message": "username has already been taken, try another one", "refer_account":refer_account})
            except User.DoesNotExist:
                user = User.objects.create_user(request.POST["username"], password=request.POST["password1"], email=request.POST["e_mail"])
                balance = user.balance.create()
                balance.balance = int(request.POST["balance"])
                if "refer_account" in request.POST:
                    balance.balance = balance.balance + 5
                    if User.objects.filter(username = request.POST["refer_account"]):
                        refer_user = User.objects.get(username = request.POST["refer_account"])
                        refer_user_balance = refer_user.balance.all()[0]
                        refer_user_balance.balance += 5
                        refer_user_balance.save()
                balance.save()
                login(request, user)
                return render(request, "accounts/signup.html")
    else:
        full_url = (request.build_absolute_uri())
        if (full_url.find("/?account=") != -1):
            refer_account = full_url[(full_url.find("/?account=") + len("/?account=")) :]
            if User.objects.filter(username = refer_account):
                return render(request, "accounts/signup.html", {"refer_account":refer_account})
        return render(request, "accounts/signup.html")

def Login(request):
    if request.method == "POST":
        user = authenticate(username=request.POST["username"], password=request.POST["password"])
        if user is not None:
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST["next"])
            return redirect('home')
        else:
            return render(request, "accounts/login.html", {"message": "the user name and password did not match"})
    else:
        return render(request, "accounts/login.html")

def Logout(request):
    if request.method == "POST":
        logout(request)
        return render(request, "accounts/login.html")

@login_required
def account_detail(request):
    return render(request, "accounts/account_detail.html", {"user":request.user, "amount":request.user.balance.all()[0].balance})

@login_required
def charge_account(request):
    balance = request.user.balance.all()[0]
    if int(request.POST["charge_amount"]) > 0:
        balance.balance += int(request.POST["charge_amount"])
        balance.save()
    return render(request, "accounts/account_detail.html", {"user":request.user, "amount":request.user.balance.all()[0].balance})
