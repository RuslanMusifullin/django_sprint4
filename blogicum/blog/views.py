from django.shortcuts import render, get_object_or_404, redirect

from blog.models import Post, Category, Comment

from datetime import date

from django.urls import reverse_lazy, reverse

from django.contrib.auth.models import User

from django.db.models import Q

from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView)

from .forms import PostForm, UserForm, CommentForm

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator

from .utils import comment_count

QUANTITY_POSTS_MAIN_SCREEN = 5


def index(request):
    template = 'blog/index.html'
    posts = Post.objects.select_related(
        'author', 'category', 'location'
    ).filter(
        pub_date__date__lt=date.today(), is_published=True,
        category__is_published=True).order_by('id')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print(type(page_obj[3]))
    # comment_count = comment_count(pk)
    context = {'page_obj': page_obj}
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'blog/detail.html'
    post = Post.objects.get(pk=post_id)
    context = {'post': post}
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.filter(is_published=True), slug=category_slug)
    category_posts = category.posts.filter(
        pub_date__date__lt=date.today(), is_published=True,)
    paginator = Paginator(category_posts, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'category': category,
               'page_obj': page_obj}
    return render(request, template, context)


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('blog:profile', kwargs={
            'user_name': self.request.user.username}) 


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/post_form.html'


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context 


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('blog:index')


def profile_details(request, user_name):
    template = 'blog/profile_detail.html'
    profile = User.objects.get(username=user_name)
    user_posts = profile.posts.all().order_by('id')
    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'profile': profile,
               'page_obj': page_obj}
    return render(request, template, context)


def profile_edit(request):
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
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
