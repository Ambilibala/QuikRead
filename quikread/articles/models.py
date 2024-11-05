from django.db import models
from feeds.models import Source
from django.conf import settings
from django.utils import timezone

# Create your models here.
class Article(models.Model):

    title = models.CharField(max_length=1000)
    html_content = models.TextField()
    text_summary = models.TextField()
    thumbnail_url = models.URLField(max_length=500,blank=True, null=True)
    article_url = models.URLField(max_length=500,unique=True)
    published_date = models.DateTimeField()
    
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title
    
class UserArticle(models.Model):
    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE,related_name='user_article')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unread')
    fetched_date = models.DateTimeField(default=timezone.now) 
    read_date = models.DateTimeField(null=True, blank=True)


    class Meta:
        unique_together = ('user', 'article')
    def __str__(self):
        return f"{self.user.username} - {self.article.title} - {self.status}"
    def mark_as_read(self):
        self.status = 'read'
        self.read_date = timezone.now()
        self.save()
    def mark_as_unread(self):
        self.status = 'unread'
        self.read_date = None
        self.save()
    
class SavedArticle(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    saved_date = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('user', 'article')

    def __str__(self):
        return f"{self.user.username} - {self.article.title}"