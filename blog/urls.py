from django.conf.urls  import url

from . import views

app_name = 'blog'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    # url(r'^index.html$', views.index, name='index'),
    url(r'^post/(?P<pk>[0-9]+)/$', views.PostDetailView.as_view(), name='detail'),
    url(r'^archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$', views.ArchiveView.as_view(), name='archives'),
    url(r'^categories/(?P<pk>[0-9]+)/$', views.CategoryView.as_view(), name='categories'),
    url(r'^tags/(?P<pk>[0-9]+)/$', views.TagView.as_view(), name='tags'),
    url(r'^blog/$', views.BlogView.as_view(), name='blog'),
    url(r'^about/$', views.AboutView.as_view(), name='about'),
    url(r'^contact/$', views.ContactView.as_view(), name='contact'),
    url(r'^search/$', views.search, name='search'),
]