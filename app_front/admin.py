from django.contrib import admin
from app_front.models import CallbackForm
from app_bot.tasks import send_bf_gif


def super_action(modeladmin, request, queryset):
    send_bf_gif.delay()

@admin.register(CallbackForm)
class AdminCallbackForm(admin.ModelAdmin):
    actions = [super_action]
    list_display = ['email', 'connect', 'name', 'message']