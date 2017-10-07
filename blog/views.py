# coding: utf-8
import markdown
from markdown.extensions.toc import TocExtension

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.text import slugify
from django.db.models import Q


from .models import Post, Category, Tag

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

    context = {'post_list': post_list,
               'paginator': paginator,
               'current_page': page,
               }

    return render(request, 'blog/index.html', context=context)


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 1

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')
        pagination_data = self.pagination_data(paginator, page, is_paginated)

        context.update(pagination_data)

        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            return {}

        left = []
        right = []

        left_has_more = False
        right_has_more = False

        first = False
        last = False

        cpage = page.number

        total_pages = paginator.num_pages
        page_range = [li for li in paginator.page_range]

        if cpage == 1:
            right = page_range[cpage: cpage + 2]

            if right[-1] < total_pages - 1:
                right_has_more = True

            if right[-1] < total_pages:
                last = True

        elif cpage == total_pages:

            left = page_range[(cpage - 3) if (cpage - 3) > 0 else 0:cpage - 1]

            if left[0] > 2:
                left_has_more = True

            if left[0] > 1:
                first = True
        else:

            left = page_range[
                (cpage - 3) if (cpage - 3) > 0 else 0:cpage - 1]
            right = page_range[cpage:cpage + 2]

            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

        data = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }

        return data


def archives(request, year, month):
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month
                                    )
    return render(request, 'blog/index.html', context={'post_list': post_list})


class ArchiveView(IndexView):

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchiveView, self).get_queryset().filter(created_time__year=year,
                                                              created_time__month=month)


def categories(request, pk):
    post_list = Post.objects.filter(category=pk)
    return render(request, 'blog/index.html', context={'post_list': post_list})


class CategoryView(IndexView):

    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)


def tags(request, pk):
    post_list = Post.objects.filter(tags=pk)
    return render(request, 'blog/index.html', context={'post_list': post_list})


class TagView(IndexView):

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=tag)

# def to_page(request, page):
#     post_list = Post.objects.all()
#     post_list, paginator = make_page(post_list, page)

#     context={'post_list': post_list,
#              'paginator': paginator,
#              'current_page': page,
#             }

#     return render(request, 'blog/index.html', context=context)


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

    context = {'post': post,
               'form': form,
               'comment_list': comment_list,
               }

    return render(request, 'blog/detail.html', context=context)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        response = super(PostDetailView, self).get(request, *args, **kwargs)
        self.object.increase_views()

        return response

    def get_object(self, queryset=None):
        post = super(PostDetailView, self).get_object(queryset=None)
        md = markdown.Markdown(       extensions=[
                                          'markdown.extensions.extra',
                                          'markdown.extensions.codehilite',
                                          # 'markdown.extensions.toc',
                                          TocExtension(slugify=slugify),

                                      ])
        post.body = md.convert(post.body)
        post.toc = md.toc

        return post

    def get_context_data(self, **kwargs):

        context = super(PostDetailView, self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'form': form,
            'comment_list': comment_list
        })
        return context

def search(request):
    q = request.GET.get('q')
    error_msg = ''

    if not q:
        error_msg = "请输入关键词"
        return render(request, 'blog/index.html', {'error_msg': error_msg})

    post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))

    return render(request, 'blog/index.html', {'error_msg': error_msg,
                                                'post_list': post_list})