from django.contrib.syndication.views import Feed
from .models import Post

class AllPostsRssFeed(Feed):
    """docstring for AllPostsRssFeed"""
    title = "Shellder"

    link = "/"

    description = "My blogs"

    def items(self):
        return Post.objects.all()

    def item_title(self, item):
        return '[%s] %s' % (item.category, item.title)

    def item_description(self, item):
        return item.body