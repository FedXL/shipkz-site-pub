from django.contrib import admin
from django.db import models
from app_bot.management.bot_core import web_open_meeting_message_in_bot
from .models import (
    Buyers, Discounts,
    Documents, EmailTask, Exchange, FastAnswers,
    Jwt, Managers, Messages, OrderStatus, OrderStatusInfo, Orders, ParceTask,
    Photos, Posts, RootUsers, Services, Users, UsersApp, WebDocs,
    WebMessages, WebPhotos, WebUsers, WebUsersMeta, Websockets, WebsocketsSupport, OrderItem
)

class ReadOnlyAdminMixin:
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        for field in self.model._meta.fields:
            if isinstance(field, models.ForeignKey):
                readonly_fields += (field.name,)
        return readonly_fields

class BuyersAdmin( admin.ModelAdmin):
    list_display = [field.name for field in Buyers._meta.fields]

class DiscountsAdmin( admin.ModelAdmin):
    list_display = [field.name for field in Discounts._meta.fields]

class DocumentsAdmin( admin.ModelAdmin):
    list_display = [field.name for field in Documents._meta.fields]

class EmailTaskAdmin( admin.ModelAdmin):
    list_display = [field.name for field in EmailTask._meta.fields]

class OrderItemAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OrderItem._meta.fields]



class ExchangeAdmin( admin.ModelAdmin):
    list_display = [field.name for field in Exchange._meta.fields]

class FastAnswersAdmin( admin.ModelAdmin):
    list_display = [field.name for field in FastAnswers._meta.fields]

class JwtAdmin( admin.ModelAdmin):
    list_display = [field.name for field in Jwt._meta.fields]

class ManagersAdmin( admin.ModelAdmin):
    list_display = [field.name for field in Managers._meta.fields]

class MessagesAdmin( admin.ModelAdmin):
    list_display = [field.name for field in Messages._meta.fields]
    search_fields = ['storage__user_id','message_body']

class OrderStatusAdmin( admin.ModelAdmin):
    list_display = [field.name for field in OrderStatus._meta.fields]
    search_fields = ['order__id']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0



class OrderStatusInfoAdmin( admin.ModelAdmin):

    list_display = ['id',
                    'order',
                    'is_forward',
                    'host_country',
                    'paid',
                    'arrived_to_forward',
                    'got_track',
                    'arrived_to_host_country',
                    'received_in_host_country',
                    'send_to_ru',
                    'success',
                    'shop',
                    'cdek',
                    'trek',
                    'store_order_number']

    fields = ['order',
              'is_forward',
              'host_country',
              'paid',
              'arrived_to_forward',
              'got_track',
              'arrived_to_host_country',
              'received_in_host_country',
              'send_to_ru',
              'success','shop','cdek','trek', 'store_order_number']
    search_fields = ['order__id']

class OrdersAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ['id', 'group', 'client', 'web_user', 'type', 'time', 'status', 'user_ip']
    fields = ['group', 'client', 'web_user', 'type', 'status', 'user_ip', 'body']
    search_fields = ['id', 'web_user__web_username']
    readonly_fields = ['body']
    autocomplete_fields = ['group','client', 'web_user']

class ParceTaskAdmin( admin.ModelAdmin):
    list_display = [field.name for field in ParceTask._meta.fields]

class PhotosAdmin( admin.ModelAdmin):
    list_display = [field.name for field in Photos._meta.fields]

class PostsAdmin( admin.ModelAdmin):
    list_display = [field.name for field in Posts._meta.fields]

class RootUsersAdmin( admin.ModelAdmin):
    list_display = [field.name for field in RootUsers._meta.fields]

class ServicesAdmin( admin.ModelAdmin):
    list_display = [field.name for field in Services._meta.fields]

class UsersAdmin( admin.ModelAdmin):
    search_fields = ['user_id', 'user_name']
    list_display = [field.name for field in Users._meta.fields]

class UsersAppAdmin( admin.ModelAdmin):
    list_display = [field.name for field in UsersApp._meta.fields]

class WebDocsAdmin( admin.ModelAdmin):
    list_display = [field.name for field in WebDocs._meta.fields]

class WebMessagesAdmin( admin.ModelAdmin):
    list_display = ['id', 'message_body', 'is_answer', 'user', 'message_type', 'is_read']

class WebPhotosAdmin( admin.ModelAdmin):
    list_display = [field.name for field in WebPhotos._meta.fields]

def open_bot_meeting_message(modeladmin, request, queryset):
    for web_user in queryset:
        web_open_meeting_message_in_bot(web_user=web_user)

class WebUsersAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ['user_id', 'user_name', 'web_username']
    actions = [open_bot_meeting_message]
    search_fields = ['web_username', 'user_id']

class WebUsersMetaAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in WebUsersMeta._meta.fields]

class WebsocketsAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in Websockets._meta.fields]

class WebsocketsSupportAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = [field.name for field in WebsocketsSupport._meta.fields]


admin.site.register(Buyers, BuyersAdmin)
admin.site.register(Discounts, DiscountsAdmin)
admin.site.register(Documents, DocumentsAdmin)
admin.site.register(EmailTask, EmailTaskAdmin)
admin.site.register(Exchange, ExchangeAdmin)
admin.site.register(FastAnswers, FastAnswersAdmin)
admin.site.register(Jwt, JwtAdmin)
admin.site.register(Managers, ManagersAdmin)
admin.site.register(Messages, MessagesAdmin)
admin.site.register(OrderStatus, OrderStatusAdmin)
admin.site.register(OrderStatusInfo, OrderStatusInfoAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(ParceTask, ParceTaskAdmin)
admin.site.register(Photos, PhotosAdmin)
admin.site.register(Posts, PostsAdmin)
admin.site.register(RootUsers, RootUsersAdmin)
admin.site.register(Services, ServicesAdmin)
admin.site.register(Users, UsersAdmin)
admin.site.register(UsersApp, UsersAppAdmin)
admin.site.register(WebDocs, WebDocsAdmin)
admin.site.register(WebMessages, WebMessagesAdmin)
admin.site.register(WebPhotos, WebPhotosAdmin)
admin.site.register(WebUsers, WebUsersAdmin)
admin.site.register(WebUsersMeta, WebUsersMetaAdmin)
admin.site.register(Websockets, WebsocketsAdmin)
admin.site.register(WebsocketsSupport, WebsocketsSupportAdmin)