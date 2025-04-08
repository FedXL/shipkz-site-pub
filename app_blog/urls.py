from django.urls import path
from app_blog.views import BlogHomeView, BlogArcticleView



urlpatterns= [
    path('', BlogHomeView.as_view(), name='blog_home'),
    path('articles/<slug:slug>/', BlogArcticleView.as_view(), name='blog_article'),
    ]
