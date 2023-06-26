from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from blog.models import Post, Category

NUM_OF_PUNBLIC = 5


def index(request):
    template = 'blog/index.html'
    post_list = Post.objects.select_related(
        'category',
        'location',
        'author'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )[:NUM_OF_PUNBLIC]
    context = {'post_list': post_list}
    return render(request, template, context)


def post_detail(request, id):
    template = 'blog/detail.html'
    post_list = get_object_or_404(Post.objects.select_related(
        'location', 'author', 'category').filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
    ),
        pk=id
    )
    context = {'post': post_list}
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(Category,
                                 slug=category_slug,
                                 is_published=True)
    post_list = Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category=category
    )
    context = {'category': category, 'post_list': post_list}
    return render(request, template, context)
