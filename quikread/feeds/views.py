from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from feeds.models import Source, UserSubscription
# Create your views here.
def home_page(request):
    return render(request,'home_page.html')
def display_sources(request):
    sources = Source.objects.all()
    return render(request,'sources_page.html',{'sources':sources})
@login_required
def subscribe_feed(request, source_id):
    source = get_object_or_404(Source, id=source_id)
    user = request.user

    UserSubscription.objects.get_or_create(user=user, source=source)
    return redirect('source_list')  # Redirect to a relevant view after subscribing
