from django.contrib import admin
from django.urls import path, include

from app_front.views import YandexVerification

admin.site.site_header = 'ShipKZ Admin'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_front.urls')),
    path('auth/', include('app_auth.urls')),
    path('panel/', include('panel.urls')),
    path('api/v1/',include('app_api.urls')),
    path('captcha/', include('captcha.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('yandex_50e907a0d24e53ea.html', YandexVerification.as_view(), name='yandex-verification'),
]