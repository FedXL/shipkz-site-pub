from cachetools.func import lru_cache
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from app_blog.models import Article


class BlogHomeView(ListView):
    model = Article
    template_name = 'pages/blog-home.html'
    context_object_name = 'articles'
    paginate_by = 9
    ordering = ['-created_at']


@lru_cache(maxsize=2)
def get_article_context(slug):
    article_object = Article.objects.filter(name=slug).first()
    if not article_object:
        return None
    context = {
        "title": article_object.title,
        "photo_title": article_object.photo_title,
        "content": article_object.content,
        "created_at": article_object.created_at
    }
    return context


class BlogArticleView(View):
    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        article_context = get_article_context(slug)
        if not article_context:
            return HttpResponseNotFound("Article not found")
        return render(request, template_name='pages/blog-article.html', context=article_context)