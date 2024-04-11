from django.db import models
from django.db.models import Count
from django.utils import timezone


class PublishedQuerySet(models.QuerySet):
    """Менеджер публикации."""

    def filter_posts_for_publication(self):
        return self.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        )

    def count_comments(self):
        return self.select_related(
            'category', 'location', 'author'
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')