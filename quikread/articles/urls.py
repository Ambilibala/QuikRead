from django.urls import path
from . import views
urlpatterns = [
    path('show_articles',views.view_articles,name = 'feed_page'),
    path('show_article_content/<article_id>',views.view_article_content,name = 'article_content'),
    path('feed_by_category/<category_id>',views.articles_by_category,name='feed_by_category'),
    path('save_article/<article_id>',views.save_article,name = 'save_article'),
    path('unsave_article/<article_id>',views.unsave_article,name = 'unsave_article'),
    path('show_saved_articles',views.show_saved_articles,name = 'show_saved_articles'),
    path('mark_read/<article_id>',views.mark_article_as_read,name = 'mark_article_as_read'),
    path('mark_unread/<article_id>',views.mark_article_as_unread,name = 'mark_article_as_unread')
]