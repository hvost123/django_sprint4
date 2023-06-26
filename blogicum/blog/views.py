from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render, redirect
import datetime as dt

from blog.models import Post, Category, Comment
from django.contrib.auth.models import User
from blog.forms import PostForm, CommentForm, ProfileForm


class ProfileLoginView(LoginView):
    def get_success_url(self):
        url = reverse(
            'blog:profile',
            args=(self.request.user.get_username(),)
        )
        return url


def edit_profile(request, name):
    templates = 'blog/user.html'
    instance = get_object_or_404(User, username=name)
    if instance.username != request.user.username:
        return redirect('login')
    form = ProfileForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
    return render(request, templates, context)


def info_profile(request, name):
    templates = 'blog/profile.html'
    user = get_object_or_404(
        User,
        username=name,
    )
    profile_post = user.posts.all()
    paginator = Paginator(profile_post, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile': user,
        'page_obj': page_obj,
    }
    return render(request, templates, context)


class PostListView(ListView):
    template_name = 'blog/index.html'
    current_time = dt.datetime.now()
    model = Post
    queryset = Post.objects.filter(
        is_published=True,
        pub_date__lte=current_time,
        category__is_published=True
    ).select_related('author')
    ordering = '-pub_date'
    paginate_by = 10


def category_posts(request, category_slug):
    templates = 'blog/category.html'
    current_time = dt.datetime.now()
    category = get_object_or_404(
        Category,
        is_published=True,
        slug=category_slug
    )
    post_list = category.posts.filter(
        pub_date__lte=current_time,
        is_published=True,
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, templates, context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        if self.request.user.is_authenticated:
            url = reverse(
                'blog:profile',
                args=(self.request.user.get_username(),)
            )
        else:
            url = reverse('login')
        return url


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.p_id = kwargs['pk']
        instance = get_object_or_404(Post, pk=self.p_id)
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=self.p_id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        url = reverse('blog:post_detail', args=[str(self.p_id)])
        return url


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comment.select_related(
                'author'
            )
        )
        return context


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(request, c_id, p_id):
    instance = get_object_or_404(Comment, id=c_id, post_id=p_id)
    if instance.author != request.user:
        return redirect('login')
    form = CommentForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'comment': instance
    }
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', pk=p_id)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, c_id, p_id):
    instance = get_object_or_404(Comment, id=c_id, post_id=p_id)
    if instance.author != request.user:
        return redirect('login')
    context = {
        'comment': instance
        }
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', pk=p_id)
    return render(request, 'blog/comment.html', context)
