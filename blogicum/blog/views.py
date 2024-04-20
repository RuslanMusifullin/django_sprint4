from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone

from blog.models import Post, Category, Comment
from .forms import PostForm, UserForm, CommentForm
from core.utils import filter_posts, paginate

from django.contrib.auth.models import User
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse

PAGINATE_STEP = 10


class OnlyAuthorMixin(UserPassesTestMixin):
    """Миксин проверки авторства объекта действий"""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class IndexListView(LoginRequiredMixin, ListView):
    """CBV для главной страницы сайта, отображает все публикации"""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATE_STEP

    def get_queryset(self):
        posts = filter_posts(Post.objects)
        extended_set = posts.annotate(comment_count=Count('comments'))
        return extended_set


@login_required
def post_detail(request, post_id):
    """Функция для отображения отдельного поста"""
    template = 'blog/detail.html'
    post = get_object_or_404(Post, pk=post_id)
    category_id = post.category_id
    category = Category.objects.get(pk=category_id)
    form = CommentForm()
    comments = post.comments.all()
    context = {'post': post,
               'comments': comments,
               'form': form}
    if request.user == post.author:
        return render(request, template, context)
    else:
        if post.is_published and post.pub_date < timezone.now()\
                and category.is_published:
            return render(request, template, context)
        else:
            return HttpResponse('Страница не найдена', status=404)


class PostCreateView(LoginRequiredMixin, CreateView):
    """CBV для создания публикации"""

    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username})


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    """CBV редактирования публикации"""

    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/post_form.html'

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            post_id=self.kwargs[self.pk_url_kwarg],
        )


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """CBV удаления публикации"""

    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('blog:index')


@login_required
def category_posts(request, category_slug):
    """Функция для отображения категорий публикаций"""
    template = 'blog/category.html'
    category = get_object_or_404(
        Category, is_published=True, slug=category_slug)
    category_posts = filter_posts(category.posts)
    category_posts_ext = category_posts.annotate(
        comment_count=Count('comments'))
    paginator = paginate(category_posts_ext, PAGINATE_STEP)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'category': category,
               'page_obj': page_obj}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Функция для добавления коммментария для публикации"""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def comment_edit(request, post_id, comment_id):
    """Функция для редактирования коммментария публикации"""
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    form = CommentForm(request.POST or None,
                       instance=comment)
    context = {'form': form,
               'comment': comment}
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def comment_delete(request, post_id, comment_id):
    """Функция для удаления коммментария публикации"""
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    context = {'comment': comment}
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', context)


def profile_details(request, username):
    """Функция для просмотра профиля пользователя"""
    template = 'blog/profile.html'
    profile = get_object_or_404(User, username=username)
    all_posts = profile.posts.all().order_by('-pub_date')
    if request.user == profile:
        user_posts = all_posts
    else:
        user_posts = filter_posts(all_posts)
    user_posts_ext = user_posts.annotate(comment_count=Count('comments'))
    paginator = paginate(user_posts_ext, PAGINATE_STEP)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'profile': profile,
               'page_obj': page_obj}
    return render(request, template, context)


@login_required
def profile_edit(request):
    """Функция для редактирования профиля пользователя"""
    template = 'blog/user.html'
    instance = get_object_or_404(User, username=request.user)
    form = UserForm(
        request.POST or None,
        instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user)
    return render(request, template, context)
