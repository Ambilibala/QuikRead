from django.shortcuts import render,get_object_or_404,redirect
from .models import UserArticle,Article,SavedArticle
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse

# Create your views here.
@login_required
def view_articles(request):
    user_articles = UserArticle.objects.filter(user=request.user).order_by('-article__published_date')
    articles = [{'article': user_article.article, 'status': user_article.status} for user_article in user_articles]
    return render(request, 'feed_page.html', {'articles': articles})

@login_required
def articles_by_category(request, category_id):
    user_articles = UserArticle.objects.filter(user = request.user, article__source__category_id = category_id).order_by('-article__published_date')[:300]
    articles = [{'article': user_article.article, 'status': user_article.status} for user_article in user_articles]
    return render(request, 'feed_page.html', {'articles': articles})

@login_required
def view_article_content(request,article_id):
    user_article = get_object_or_404(UserArticle, user=request.user, article_id=article_id)
    user_article.mark_as_read()
    article = user_article.article
    is_saved = SavedArticle.objects.filter(user = request.user, article = user_article.article).exists()
    context = {'article': article,'is_saved':is_saved,'user_article':user_article}
    return render(request, 'article_content.html', context)
@login_required
def save_article(request, article_id):
    article = get_object_or_404(Article, id = article_id)
    saved_article,created = SavedArticle.objects.get_or_create(user = request.user, article = article)
    saved_article.saved_date = timezone.now()
    saved_article.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'saved'})
    return redirect('article_content',article_id = article_id)
@login_required
def unsave_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    saved_article = SavedArticle.objects.filter(user=request.user, article=article).first()
    if saved_article:
        saved_article.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'unsaved'})
    return redirect('article_content',article_id = article_id)
@login_required
def show_saved_articles(request):
    saved_articles = SavedArticle.objects.filter(user = request.user).order_by('-saved_date')
    articles = []
    for saved_article in saved_articles:
        user_article = UserArticle.objects.filter(user = request.user, article = saved_article.article).first()
        if user_article:
            status = user_article.status
            articles.append({'article': saved_article.article, 'status': status})
    return render(request, 'feed_page.html', {'articles': articles})

@login_required
def mark_article_as_read(request, article_id):
    user_article = get_object_or_404(UserArticle, user=request.user, article_id=article_id)
    user_article.mark_as_read()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'read'})
    return redirect('article_content', article_id=article_id)

@login_required
def mark_article_as_unread(request, article_id):
    user_article = get_object_or_404(UserArticle, user=request.user, article_id=article_id)
    user_article.mark_as_unread()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'unread'})
    return redirect('article_content', article_id=article_id)
