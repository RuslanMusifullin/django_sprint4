from django.utils import timezone


def filter_posts(object_set):

    return object_set.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).order_by('-pub_date')