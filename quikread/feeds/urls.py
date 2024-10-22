from django.urls import path
from . import views
urlpatterns = [
    path('',views.home_page,name='home'),
    path('source_list',views.display_sources,name='source_list'),
    path('subscribe/<source_id>',views.subscribe_feed, name = 'subscribe')
]