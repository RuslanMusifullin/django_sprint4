from .models import Post


def comment_count(pk):
    return Post.objects.get(pk=pk).comments.count()