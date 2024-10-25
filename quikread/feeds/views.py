from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from feeds.models import Source, UserSubscription,Category
from articles.models import Article,UserArticle
# Create your views here.
def home_page(request):
    return render(request,'home_page.html')
def display_sources(request):
    sources = Source.objects.all()
    user_subscriptions = UserSubscription.objects.filter(user=request.user).values_list('source_id', flat=True)
    source_info = [
        {
            'id': source.id,
            'name': source.name,
            'is_subscribed': source.id in user_subscriptions
        } for source in sources
    ]
    # print(source_info)
    return render(request, 'sources_page.html', {'source_info': source_info})

@login_required
def subscribe_feed(request, source_id):
    source = get_object_or_404(Source, id=source_id)
    user = request.user

    UserSubscription.objects.get_or_create(user=user, source=source)
    return redirect('source_list')  # Redirect to a relevant view after subscribing
@login_required
def unsubscribe_feed(request, source_id):
    source = get_object_or_404(Source, id=source_id)
    
    # Remove UserSubscription
    UserSubscription.objects.filter(user=request.user, source=source).delete()
    
    # Get all articles from the source
    articles = Article.objects.filter(source=source)
    
    # Remove UserArticle objects related to these articles for the user
    UserArticle.objects.filter(user=request.user, article__in=articles).delete()
    
    # Delete all articles from the source
    # articles.delete()
    
    return redirect('source_list')

