from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404, redirect

from blog.models import Post, Category, Comment

from django.utils import timezone

from django.urls import reverse_lazy, reverse

from django.contrib.auth.models import User

from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView)

from .forms import PostForm, UserForm, CommentForm

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator

from django.db.models import Count


class OnlyAuthorMixin(UserPassesTestMixin):
    """Миксин проверки авторства объекта действий"""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class IndexListView(LoginRequiredMixin, ListView):
    """CBV для главной страницы сайта, отображает все публикации"""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        posts = Post.objects.filter(
            pub_date__lte=timezone.now(), is_published=True,
            category__is_published=True).order_by('-pub_date')
        extended_set = posts.annotate(comment_count=Count('comments'))
        return extended_set


@login_required
def post_detail(request, post_id):
    """Функция для отображения отдельного поста"""
    template = 'blog/detail.html'
    post = get_object_or_404(Post, pk=post_id)
    # category_id = post.category_id
    # category = Category.objects.get(pk=category_id)
    form = CommentForm()
    comments = post.comments.all()
    context = {'post': post,
               'comments': comments,
               'form': form}
    if request.user == post.author:
        return render(request, template, context)
    else:
        if post.is_published and post.pub_date < timezone.now():
            return render(request, template, context)
        else:
            return redirect('blog:index')


class PostCreateView(LoginRequiredMixin, CreateView):
    """CBV для создания публикации"""

    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('blog:profile', kwargs={
            'user_name': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
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


class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
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
        Category.objects.filter(is_published=True), slug=category_slug)
    category_posts = category.posts.filter(
        pub_date__lte=timezone.now(), is_published=True,).order_by('-pub_date')
    category_posts_ext = category_posts.annotate(
        comment_count=Count('comments'))
    paginator = Paginator(category_posts_ext, 10)
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


@login_required
def profile_details(request, user_name):
    template = 'blog/profile_detail.html'
    profile = get_object_or_404(User, username=user_name)
    user_posts = profile.posts.all().order_by('-pub_date')
    user_posts_ext = user_posts.annotate(comment_count=Count('comments'))
    paginator = Paginator(user_posts_ext, 10)
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
        return redirect('blog:profile', user_name=request.user)
    return render(request, template, context)


# class ProfileDetailView(DetailView):
#     model = User
#     form_class = UserForm
#     template_name = 'blog/profile_detail.html'

#     def get_context_data(self, **kwargs):
#         # Получаем словарь контекста:
#         context = super().get_context_data(**kwargs)
#         context['page_obj'] = Post.objects.filter(author=User)
#         return context


# class CommentCreateView(LoginRequiredMixin, CreateView):
#     post = None
#     model = Comment
#     form_class = CommentForm
#     template_name = 'includes/comments.html'

#     def dispatch(self, request, *args, **kwargs):
#         self.birthday = get_object_or_404(Post, pk=kwargs['post_id'])
#         return super().dispatch(request, *args, **kwargs)

#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         form.instance.post = self.post_id
#         return super().form_valid(form)

#     def get_success_url(self) -> str:
#         return reverse('blog:post_detail', kwargs={
#             'post_id': self.request.user.username})


# class CommentUpdateView(OnlyAuthorMixin, UpdateView):
#     model = Comment
#     form_class = CommentForm
#     template_name = 'blog/comment.html'


# class CommentDeleteView(OnlyAuthorMixin, DeleteView):
#     model = Comment
#     template_name = 'blog/comment.html'

# class PostDetailView(DetailView):
#     model = Post
#     pk_url_kwarg = 'post_id'
#     template_name = 'blog/detail.html'

#     def get_context_data(self, *args, **kwargs):
#         context = super().get_context_data(*args, **kwargs)
#         context['form'] = CommentForm()
#         context['comments'] = (
#             self.object.comments.select_related('author')
#         )
#         return context

# class ProfileDetailView(DetailView):
#     model = User
#     pk_url_kwarg = 'user_name'
#     template_name = 'blog/profile_detail.html'
#     paginate_by = 10

#     def get_queryset(self):
#         page_obj = Post.objects.all().order_by('-pub_date')
#         return page_obj

    # def get_context_data(self, *args, **kwargs):
    #     context = super().get_context_data(*args, **kwargs)
    #     context['profile'] = User.objects.get(username=username)
    #     context['comments'] = (
    #         self.object.comments.select_related('author')
    #     )
    #     return context
