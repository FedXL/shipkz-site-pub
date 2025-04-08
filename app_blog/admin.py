from django.contrib import admin

from app_blog.models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('name','title', 'created_at', 'updated_at')
    search_fields = ('title','name')