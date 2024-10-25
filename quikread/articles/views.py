from django.shortcuts import render,get_object_or_404
from .models import UserArticle,Article
from django.contrib.auth.decorators import login_required

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
    return render(request, 'article_content.html', {'article': article})
