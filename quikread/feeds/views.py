from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from feeds.models import Source, UserSubscription,Category,Language
from articles.models import Article,UserArticle
from django.shortcuts import render, redirect
from articles.tasks import fetch_all_articles

# Create your views here.
def home_page(request): # You can customize the values as needed
    return render(request, 'home_page.html')
    # return render(request,'home_page.html')
def display_sources(request):
    # Fetch all languages
    languages = Language.objects.all()

    # Create a list to hold the language, category, and sources information
    language_info = []

    # Get the user's subscriptions to check if they're subscribed to a source
    user_subscriptions = UserSubscription.objects.filter(user=request.user).values_list('source_id', flat=True)

    # Loop through each language and get categories and sources
    for language in languages:
        # Get all categories related to the language (many-to-many relation)
        categories = Category.objects.all()
        category_info = []

        for category in categories:
            # Get all sources related to this category
            sources = Source.objects.filter(language = language,category = category)
            category_info.append({
                'category': category,
                'sources': sources
            })

        language_info.append({
            'language': language,
            'categories': category_info
        })
    print(language_info)
    return render(request, 'sources_page.html', {
        'language_info': language_info,
        'user_subscriptions': user_subscriptions
    })
@login_required
def subscribe_feed(request, source_id):
    source = get_object_or_404(Source, id=source_id)
    user = request.user

    UserSubscription.objects.get_or_create(user=user, source=source)
    fetch_all_articles.delay()
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

