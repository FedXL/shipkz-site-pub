from django.urls import path
from app_blog.views import BlogHomeView, BlogArticleView



urlpatterns= [
    path('', BlogHomeView.as_view(), name='blog_home'),
    path('articles/<slug:slug>/', BlogArticleView.as_view(), name='blog_article'),
    ]
