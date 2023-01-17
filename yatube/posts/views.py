from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Group, Post, User
from .forms import PostForm
from .utils import get_page_context


NUMBER_OF_OBJECTS = 10


def index(request):
    posts = Post.objects.select_related('group', 'author')
    context = get_page_context(posts, request)
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    template = "posts/group_list.html"
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {'group': group,
               }
    context.update(get_page_context(posts, request))
    return render(request, template, context)


def profile(request, username):
    """Страница профайла пользователя"""
    """на ней будет отображаться информация об авторе и его посты"""
    """код запроса к модели и создание словаря контекста"""
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    context = {
        'author': author,
    }
    context.update(get_page_context(posts, request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Страница для просмотра отдельного поста"""
    """код запроса к модели и создание словаря контекста"""
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('posts:profile', request.user)
        return render(request, 'posts/create_post.html',
                      {'form': form})
    form = PostForm()
    return render(request, 'posts/create_post.html',
                  {'form': form})


@login_required
def post_edit(request, post_id):
    """Страница редактирования постов"""
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if post.author == request.user:
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
        )
    return render(request, 'posts/create_post.html', context)
