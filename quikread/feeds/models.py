from django.db import models
from django.conf import settings

# Create your models here.
class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
class Category(models.Model):
    name = models.CharField(max_length = 100)
    language = models.ManyToManyField(Language, related_name='categories')
    def __str__(self):
        return self.name
class Source(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(unique=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, null=True,related_name='language_sources')  # Add the new Language field
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True,related_name='category_sources')
    def __str__(self):
        return self.name
class UserSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) #many to one
    source = models.ForeignKey(Source, on_delete=models.CASCADE)        #many to one
    subscribed_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'source') # a user cannot have the sam entries of source twice. to maintain data integrity

    def __str__(self):
        return f"{self.user.username} - {self.source.name}"