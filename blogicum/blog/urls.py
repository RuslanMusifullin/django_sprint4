from django.urls import path

from . import views

app_name = 'blog'

# часть адреса в виде <id> - согласно ТЗ к проекту!
urlpatterns = [
    # Posts
    path('', views.index, name='index'),
    path('posts/<int:post_id>/', views.PostDetailView.as_view(),
         name='post_detail'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:post_id>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/<int:post_id>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),
    # Comments
    path('posts/<int:post_id>/comment/', views.add_comment,
         name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<comment_id>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<comment_id>/',
         views.CommentDeleteView.as_view(), name='delete_comment'),
    # Profiles
    path('profile/<user_name>/', views.profile_details, name='profile'),
    path('profile/user_name/edit/', views.profile_edit, name='edit_profile'),
]
