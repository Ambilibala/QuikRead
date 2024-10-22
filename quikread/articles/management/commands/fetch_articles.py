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

User = get_user_model()

class Command(BaseCommand):
    help = 'Fetch articles from all user-subscribed sources at once'

    def handle(self, *args, **kwargs):
        # Fetch all unique subscriptions
        subscriptions = UserSubscription.objects.select_related('user', 'source').all()

        for subscription in subscriptions:
            source = subscription.source
            print(f'Fetching articles from source: {source.name} for user: {subscription.user.username}')
            articles = self.parse_feed(source.url)
            for article_link in articles:
                if not Article.objects.filter(article_url=article_link['link']).exists():
                    parsed_article = self.parse_article(article_link)
                    article = self.create_article_object(parsed_article, source)
                    if article:
                        self.link_articles_to_users(article, subscription.user)

    def parse_feed(self, url):
        article_links = []
        feed = feedparser.parse(url)
        for entry in feed.entries:
            article_links.append({
                'link': entry.link,
                'description': entry.description
            })
        return article_links

    def parse_article(self, article_link):
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
            'description': article_link['description']
        }

    def create_article_object(self, article_data, source):
        article, created = Article.objects.get_or_create(
            article_url=article_data['article_url'],
            defaults={
                'title': article_data['title'],
                'html_content': article_data['article_html_content'],
                'text_summary': article_data['article_text'],
                'thumbnail_url': article_data['image_url'],
                'published_date': timezone.now(),
                'source': source
            }
        )

        if not created:
        # If the article already exists, update the fields
            article.title = article_data['title']
            article.html_content = article_data['article_html_content']
            article.text_summary = article_data['article_text']
            article.thumbnail_url = article_data['image_url']
            article.published_date = timezone.now()
            article.source = source
            article.save()
        return article


    def link_articles_to_users(self, article, user):
        UserArticle.objects.get_or_create(user=user, article=article)
