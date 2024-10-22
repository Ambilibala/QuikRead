from django.shortcuts import render
from .models import UserArticle
# Create your views here.
def view_articles(request):
    articles = UserArticle.objects.all()
    return render(request,'feed_page.html',{'articles':articles})
def view_article_content(request,article_id):
    article = UserArticle.objects.get(id =article_id)
    return render(request,'article_content.html',{'article':article})
