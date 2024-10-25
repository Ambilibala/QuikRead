from django.shortcuts import render,get_object_or_404,redirect
from .models import UserArticle,Article,SavedArticle
from django.contrib.auth.decorators import login_required
from django.utils import timezone
# Create your views here.
@login_required
def view_articles(request):
    user_articles = UserArticle.objects.filter(user=request.user).order_by('-article__published_date')
    articles = [user_article.article for user_article in user_articles]
    return render(request, 'feed_page.html', {'articles': articles})
@login_required
def articles_by_category(request, category_id):
    user_articles = UserArticle.objects.filter(user=request.user, article__source__category_id=category_id).order_by('-article__published_date')[:300]  # Limit to 300 articles
    articles = [user_article.article for user_article in user_articles]
    return render(request, 'feed_page.html', {'articles': articles})
@login_required
def view_article_content(request,article_id):
    user_article = get_object_or_404(UserArticle, user=request.user, article_id=article_id)
    article = user_article.article
    is_saved = SavedArticle.objects.filter(user=request.user, article=user_article.article).exists()
    context = {'article': article,'is_saved':is_saved}
    return render(request, 'article_content.html', context)
def save_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    saved_article,created = SavedArticle.objects.get_or_create(user=request.user, article=article)
    saved_article.saved_date = timezone.now()
    saved_article.save()
    return redirect('article_content',article_id = article_id)
def unsave_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    saved_article = SavedArticle.objects.filter(user=request.user, article=article).first()
    if saved_article:
        saved_article.delete()
    return redirect('article_content',article_id = article_id)
    
def show_saved_articles(request):
    saved_articles = SavedArticle.objects.filter(user=request.user).order_by('-saved_date')
    articles = [saved_article.article for saved_article in saved_articles]
    return render(request, 'feed_page.html', {'articles': articles})