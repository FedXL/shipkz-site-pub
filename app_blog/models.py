from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


class Article(models.Model):
    name = models.CharField(max_length=255, verbose_name='Артикул для поиска')
    title = models.CharField(max_length=255, verbose_name='Название статьи')
    pre_view = models.CharField(max_length=255, verbose_name='Тизер статьи',
                                null=True,
                                blank=True,
                                default=None)
    # photo_title = models.CharField(max_length=255, verbose_name='Фото плитки в статье')
    photo = models.ImageField(upload_to='articles', null=True, blank=True, verbose_name='Фото статьи')
    meta_title = models.CharField(max_length=255, verbose_name='Мета заголовок')
    content = RichTextUploadingField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

