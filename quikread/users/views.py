from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login as auth_login,logout
from django.contrib import messages
from django.contrib.auth.models import User

# Create your views here.
def show_account(request):
    context = {'register':False,
               'login':False}
    if request.POST and 'register' in request.POST:
        context['register'] = True
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = User.objects.create_user(
                username = username,
                password = password,
            )

            messages.success(request, "user registered successfully")
        except Exception as e:
            error_msg = 'Duplicate Username'
            messages.error(request,error_msg)
    if request.POST and 'login' in request.POST:
        context['login'] = True
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            auth_login(request,user)
            return redirect('source_list')
        else:
            messages.error(request, 'invalid credentails')
        
    return render(request, 'account_options.html',context)
def user_logout(request):
    logout(request)
    return redirect('home')