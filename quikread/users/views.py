from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout

# Create your views here.
def login(request):
    return redirect('home')
def logout(request):
    logout(request)
    return redirect('home')