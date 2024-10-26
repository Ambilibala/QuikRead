# articles/management/commands/fetch_articles.py

import feedparser
import requests
import html
import re
from readabilipy import simple_json_from_html_string
import newspaper
from django.core.management.base import BaseCommand
from django.utils import timezone
from feeds.models import Source, UserSubscription
from articles.models import Article, UserArticle
from django.contrib.auth import get_user_model
import logging
logger = logging.getLogger(__name__)
User = get_user_model()

from celery import current_app as celery_app

class Command(BaseCommand):
    help = 'Fetch articles from all user-subscribed sources at once'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for fetching articles')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        if not username:
            self.stdout.write(self.style.ERROR('Username is required. Use --username to specify it.'))
            return
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist.'))
            return
        subscriptions = UserSubscription.objects.filter(user=user).select_related('source').order_by('-subscribed_date')
        for subscription in subscriptions:
            logger.debug(f'Sending task for {subscription.source.url} and {user.username}')
            celery_app.send_task('articles.tasks.fetch_article', kwargs={'url': subscription.source.url, 'username': user.username})


    @staticmethod
    @celery_app.task(name='articles.tasks.fetch_article')
    def fetch_article(url=None, username=None):
        logger.debug(f'fetch_article called with url: {url}, username: {username}')
        if url is None or username is None:
            logger.error('URL or username not provided')
            return

        article_links = Command.parse_feed(url)
        logger.debug(f'Found {len(article_links)} articles')
        user = User.objects.get(username=username)
        for article_link in article_links:
            if not UserArticle.objects.filter(user=user, article__article_url=article_link['link']).exists():
                parsed_article = Command.parse_article(article_link)
                article = Command.create_article_object(parsed_article, Source.objects.get(url=url))
                if article:
                    Command.link_articles_to_users(article, user)

    @staticmethod
    def parse_feed(url):
        print(f'Parsing feed from {url}')
        article_links = []
        feed = feedparser.parse(url)
        for entry in feed.entries:
            article_links.append({
                'link': entry.link,
                'description': entry.description
            })
        return article_links

    @staticmethod
    def parse_article(article_link):
        print(f'Parsing article {article_link["link"]}')
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        }
        req = requests.get(article_link['link'], headers=headers)
        req.encoding = 'utf-8'
        content = req.text
        article_news = newspaper.article(article_link['link'])
        article = simple_json_from_html_string(content, use_readability=True)
        article_content = article['content']
        article_title = article['title']
        article_text = article['plain_text']
        cleaned_content = html.unescape(article_content)
        cleaned_content = re.sub(r'â', "'", cleaned_content)
        cleaned_content = re.sub(r'â', '"', cleaned_content)
        cleaned_content = re.sub(r'â¦', '...', cleaned_content)
        cleaned_content = re.sub(r'â', '', cleaned_content)
        print(article_news.top_image)
        return {
            'title': article_title,
            'article_html_content': cleaned_content,
            'article_text': article_text,
            'article_url': article_link['link'],
            'image_url': article_news.top_image,
            'published_date': article_news.publish_date,
            
            'description': article_link['description']
        }

    @staticmethod
    def create_article_object(article_data, source):
        print(f'Creating article object for {article_data["title"]}')
        article, created = Article.objects.get_or_create(
            article_url=article_data['article_url'],
            defaults={
                'title': article_data['title'],
                'html_content': article_data['article_html_content'],
                'text_summary': article_data['article_text'],
                'thumbnail_url': article_data['image_url'],
                'published_date': article_data.get('published_date', timezone.now()),
                'source': source
            }
        )
        if not created:
            article.title = article_data['title']
            article.html_content = article_data['article_html_content']
            article.text_summary = article_data['article_text']
            article.thumbnail_url = article_data['image_url']
            article.published_date = article_data['published_date']
            article.source = source
            article.save()
        return article

    @staticmethod
    def link_articles_to_users(article, user):
        print(f'Linking article {article.title} to user {user.username}')
        UserArticle.objects.get_or_create(user=user, article=article,fetched_date = timezone.now())


