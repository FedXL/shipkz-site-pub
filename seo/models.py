from django.db import models

class ShopCategory(models.Model):
    name = models.CharField(max_length=255, unique=True,verbose_name='Название в базе')
    name_rus = models.CharField(max_length=255, unique=True,verbose_name="Название на сайте")
    image = models.ImageField(upload_to='shop_categories', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    priority = models.IntegerField(default=10, verbose_name='Приоритет')
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория магазина"
        verbose_name_plural = "Категории магазинов"

    def to_dict(self):
        shop_items = self.shop_items.all().order_by('link_address')
        result = {
            'name': self.name,
            'name_rus': self.name_rus,
            'description': self.description,
            'shop_items': [item.to_link_dict() for item in shop_items if item],
        }
        if self.image:
            result['image'] = self.image.url
        return result

class ShopItem(models.Model):
    image = models.ImageField(upload_to='shop_links', null=True, blank=True)
    category = models.ForeignKey(ShopCategory, on_delete=models.DO_NOTHING,
                                 related_name='shop_items', null=True, blank=True)
    name = models.CharField(max_length=255, unique=True,verbose_name='Название магазина')
    link_address = models.URLField()
    link_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    is_top = models.BooleanField(default=False,verbose_name='Ссылка в пре релизе или нет')
    is_active = models.BooleanField(default=True,verbose_name='Битая ссылка или нет')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ссылка на магазин"
        verbose_name_plural = "Ссылки на магазины"

    def to_link_dict(self):
        if self.is_active:
            return {
                'name': self.name,
                'link_address': self.link_address,
                'link_name': self.link_name,
                'description': self.description,
                'country': self.country,
                'is_top': self.is_top,
                'is_active': self.is_active
            }
        else:
            return None

class Service(models.Model):
    name = models.CharField(max_length=255, unique=True,verbose_name='Сервисы')