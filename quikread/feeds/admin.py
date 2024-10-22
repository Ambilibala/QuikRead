from django.contrib import admin
from .models import Source,Category,UserSubscription
# Register your models here.
admin.site.register(Source)
admin.site.register(Category)
admin.site.register(UserSubscription)