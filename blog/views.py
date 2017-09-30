import markdown

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post

from comments.forms import CommentForm

global PAGE_NUM
PAGE_NUM = 1

def make_page(objects,  cpage, page_num=PAGE_NUM):
    paginator = Paginator(objects, page_num)
    try:
        objects = paginator.page(cpage)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        objects = paginator.page(paginator.num_pages)

    return objects, paginator


def index(request, page=1):
    # page = 1
    post_list = Post.objects.all()
    post_list, paginator = make_page(post_list, page)

    context={'post_list': post_list,
             'paginator': paginator,
             'current_page': page,
            }

    return render(request, 'blog/index.html', context=context)


def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.increase_views()

    post.body = markdown.markdown(post.body,
                                  extensions=[
                                      'markdown.extensions.extra',
                                      'markdown.extensions.codehilite',
                                      'markdown.extensions.toc',
                                  ])

    form = CommentForm()
    comment_list = post.comment_set.all()

    context={'post': post,
             'form': form,
             'comment_list': comment_list,
             }

    return render(request, 'blog/detail.html', context=context)

def archives(request, year, month):
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month
                                    )
    return render(request, 'blog/index.html', context={'post_list': post_list})

def categories(request, pk):
    post_list = Post.objects.filter(category=pk)
    return render(request, 'blog/index.html', context={'post_list': post_list})

def tags(request, pk):
    post_list = Post.objects.filter(tags=pk)
    return render(request, 'blog/index.html', context={'post_list': post_list})

# def to_page(request, page):
#     post_list = Post.objects.all()
#     post_list, paginator = make_page(post_list, page)

#     context={'post_list': post_list,
#              'paginator': paginator,
#              'current_page': page,
#             }

#     return render(request, 'blog/index.html', context=context)