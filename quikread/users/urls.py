from django.urls import path
from . import views
urlpatterns = [
    path('login',views.show_account,name = 'login'),
    path('logout',views.user_logout,name = 'logout')
]