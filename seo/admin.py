from django.contrib import admin
from seo.models import ShopCategory, ShopItem, Service
from seo.tasks import extract_links_task, extract_links_with_categories_task, add_custom_categories

class ShopItemInline(admin.TabularInline):
    model = ShopItem
    extra = 0

@admin.register(ShopCategory)
class ShopCategoryAdmin(admin.ModelAdmin):
    list_display = ('name','priority', 'name_rus', 'description')
    inlines = [ShopItemInline,]
@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ("category","link_address",'is_active')
    search_fields = ('name', 'link_name', 'country')

def category_collections(modeladmin, request, queryset):
    extract_links_with_categories_task.delay()

def add_lf_links(modeladmin, request, queryset):
    extract_links_task.delay()

def add_custom_categories_task(modeladmin, request, queryset):
    add_custom_categories.delay()

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_dispay = ('name')
    # actions = [add_lf_links,
    #            category_collections,
    #            add_custom_categories_task,]

