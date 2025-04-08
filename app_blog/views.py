from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from httplib2 import Response
from app_blog.models import Article


class BlogHomeView(ListView):
    model = Article
    template_name = 'pages/blog-home.html'
    context_object_name = 'articles'
    paginate_by = 9
    ordering = ['-created_at']


def get_article_context(slug):
    arcticle_object = Article.objects.filter(name=slug).first()
    if not arcticle_object:
        return Response(status=404)
    context = {
        "title": arcticle_object.title,
        "photo_title": arcticle_object.photo_title,
        "photo": arcticle_object.photo,
        "content": arcticle_object.content,
        "created_at": arcticle_object.created_at
    }
    return context


class BlogArcticleView(View):
    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        article_context = get_article_context(slug)
        return render(request,template_name='pages/blog-article.html', context=article_context)