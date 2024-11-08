import feedparser
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from readability import Document
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from django.utils import timezone
from feeds.models import Source, UserSubscription
from articles.models import Article, UserArticle
from django.contrib.auth import get_user_model
import logging
from celery import current_app as celery_app
from datetime import datetime

User = get_user_model()
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch articles from all user-subscribed sources asynchronously'

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

        async def async_fetch_articles():
            article_links = await Command.async_parse_feed(url)
            user = await sync_to_async(User.objects.get)(username=username)

            tasks = [
                Command.async_parse_article(link, user)
                for link in article_links 
                if not await sync_to_async(UserArticle.objects.filter(user=user, article__article_url=link['link']).exists)()
            ]
            await asyncio.gather(*tasks)

        asyncio.run(async_fetch_articles())

    @staticmethod
    async def async_parse_feed(url):
        print(f'Parsing feed from {url}')
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                feed_data = await response.text()
                feed = feedparser.parse(feed_data)
                article_links = [
                    {'source_url':url,'link': entry.link, 'description': entry.get("description", ""), 'published_date': entry.get("published", timezone.now())}
                    for entry in feed.entries
                ]
        return article_links
    @staticmethod
    def parse_published_date(date_str):
    # Convert "Sat, 02 Nov 2024 16:35:40 +0530" to Django-friendly datetime format
        try:
            dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
        except ValueError:
            # If parsing fails, use the current time as a fallback
            dt = timezone.now()
        return dt
    @staticmethod
    async def async_parse_article(article_link, user):
        print(f'Parsing article {article_link["link"]} for user {user.username}')
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(article_link['link'], headers=headers) as response:
                html_content = await response.text()
                doc = Document(html_content)
                parsed_content = doc.summary()
                
                # Use BeautifulSoup for metadata and thumbnail extraction
                soup = BeautifulSoup(html_content, "html.parser")
                og_image = soup.find("meta", property="og:image")
                twitter_image = soup.find("meta", property="twitter:image")

                thumbnail_url = og_image["content"] if og_image else twitter_image["content"] if twitter_image else None

                # Create and link the article asynchronously
                source = await Command.get_source(article_link['source_url'])
                if source:
                    article = await Command.async_create_article_object(
                        {
                            'title': doc.title(),
                            'article_html_content': parsed_content,
                            'article_text': parsed_content,
                            'article_url': article_link['link'],
                            'image_url': thumbnail_url,
                            'published_date': Command.parse_published_date(article_link.get('published_date', timezone.now())),
                            'description': article_link['description']
                        },
                        source
                    )
                    await Command.async_link_articles_to_users(article, user)

    @staticmethod
    async def get_source(url):
    # Use sync_to_async for the filter operation
        source_query = await sync_to_async(Source.objects.filter)(url=url)

        # Check if any sources exist asynchronously
        exists = await sync_to_async(source_query.exists)()
        
        # If the source exists, get the first one asynchronously
        if exists:
            return await sync_to_async(source_query.first)()
    
        return None

    @staticmethod
    async def async_create_article_object(article_data, source):
        print(f'Creating article object for {article_data["title"]}')
        article, created = await Article.objects.aget_or_create(
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
            print(f'already existing for {article_data["title"]}')
            article.title = article_data['title']
            article.html_content = article_data['article_html_content']
            article.text_summary = article_data['article_text']
            article.thumbnail_url = article_data['image_url']
            article.published_date = article_data['published_date']
            article.source = source
            await sync_to_async(article.save)()
        return article

    @staticmethod
    @staticmethod
    async def async_link_articles_to_users(article, user):
        print(f'Linking article {article.title} to user {user.username}')
        user_article, created = await UserArticle.objects.aget_or_create(
            user=user, article=article, defaults={'fetched_date': timezone.now()}
        )
        if created:
            print(f'Successfully linked article {article.title} to user {user.username}')
        else:
            print(f'Article {article.title} was already linked to user {user.username}')

