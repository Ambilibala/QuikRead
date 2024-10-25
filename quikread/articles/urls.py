from django.urls import path
from . import views
urlpatterns = [
    path('show_articles',views.view_articles,name = 'feed_page'),
    path('show_article_content/<article_id>',views.view_article_content,name = 'article_content'),
    path('feed_by_category/<category_id>',views.articles_by_category,name='feed_by_category')
]