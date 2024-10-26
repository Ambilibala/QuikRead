from celery import shared_task
from django.utils import timezone
from .models import  Article, UserArticle
from feeds.models import UserSubscription
from .management.commands.fetch_articles import Command


@shared_task
def fetch_all_articles():
    print("fetching articles...")
    command = Command()
    subscriptions = UserSubscription.objects.all().select_related('source').order_by('-subscribed_date')
    for subscription in subscriptions:
        user = subscription.user.username
        command.handle(username=user)

@shared_task
def cleanup_old_articles():
    threshold_time = timezone.now() - timezone.timedelta(hours=12)
    Article.objects.filter(article__published_date__lt=threshold_time).delete()
