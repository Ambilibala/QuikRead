from django.core.management.base import BaseCommand
from feeds.models import Source, Category,UserSubscription

class Command(BaseCommand):
    help = 'Load initial feed sources into the database'

    def handle(self, *args, **kwargs):
        sources = [
            {"name": "Times of India", "url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms", "category": "News"},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml", "category": "Tech"}
            # Add more sources here
        ]

        for source_data in sources:
            category, _ = Category.objects.get_or_create(name=source_data['category'])
            Source.objects.get_or_create(
                name=source_data['name'],
                url=source_data['url'],
                category=category
            )

            UserSubscription.objects.get_or_create(
                
            )

        # self.stdout.write(self.style.SUCCESS('Successfully loaded sources.'))
