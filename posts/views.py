from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User
from .forms import PostForm


PGR = 10


def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, PGR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(request, "index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).all()
    paginator = Paginator(posts, PGR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        "group": group,
        "posts": posts,
        'page': page,
        'paginator': paginator,
    }
    return render(request, "group.html", context)


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    form = PostForm()
    return render(request, 'new.html', {'form': form, 'is_edit': True})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, PGR)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'author': author,
        'paginator': paginator,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    text = Post._meta.get_field("text")
    post = get_object_or_404(Post, id=post_id, author=author)
    count = Post.objects.filter(author=author).select_related('author').count()
    context = {
        'post': post,
        'author': author,
        'count': count,
        'post_id': post_id,
        'text': text,
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = PostForm(request.POST or None, instance=post)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    if post.author == request.user:
        if form.is_valid():
            form.save()
            return redirect('post', username, post_id)
        return render(request, 'new.html', context)
    return redirect('post', username, post_id)
