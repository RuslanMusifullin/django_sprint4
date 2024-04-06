from django.contrib import admin
from .models import Post, Category, Location, Comment


class PostAdmin(admin.ModelAdmin):
    """Модель админки страницы постов"""

    list_display = (
        'title',
        'text',
        'is_published',
        'category',
        'location',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)


class CategoryAdmin(admin.ModelAdmin):
    """Модель админки страницы категорий"""

    list_display = (
        'title',
        'is_published',
        'description',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('category',)


class LocationAdmin(admin.ModelAdmin):
    """Модель админки страницы локаций"""

    list_display = (
        'name',
        'is_published',
    )
    list_editable = (
        'is_published',
    )


class CommentAdmin(admin.ModelAdmin):
    """Модель админки страницы комментариев"""

    list_display = (
        'text',
        'post',
        'author',
        'created_at',
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
