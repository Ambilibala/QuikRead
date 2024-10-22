from django.contrib import admin
from .models import Article,UserArticle,SavedArticle
admin.site.register(Article)
admin.site.register(UserArticle)
admin.site.register(SavedArticle)

#  Register your models here.
