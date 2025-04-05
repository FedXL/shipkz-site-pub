from django.urls import path, reverse_lazy
from django.views.generic import TemplateView, RedirectView
from app_front.views import StartingPageView, KazakhstanPageView, TradeinnPageView, AboutUsPageView, ContactsPageView, \
    TariffsPageView, LkHelloPageView, LkCreateOrderPageView, LkOrdersPageView, LkPreordersPageView, LkProfilePageView, \
    LkMessagesPageView, LkLogoutPageView, testing_view, LkOrderPageView, LkPreordersDeletePageView, CallbackFormView, \
    sitemap_view, AloneUnregPageView, VinilPageView, ShopListView

urlpatterns = [
    path('robots.txt', TemplateView.as_view(template_name='pages/robots.txt', content_type='text/plain')),
    path('sitemap.xml', sitemap_view, name='sitemap'),
    path('', StartingPageView.as_view(), name='home'),
    path('forwarding/', RedirectView.as_view(url=reverse_lazy('home'), permanent=True)),
    path('callback/', CallbackFormView.as_view(), name='callback'),
    path('test/', testing_view, name='test'),
    path('tranzit-kz/', KazakhstanPageView.as_view(), name='kazakhstan'),
    path('kazakhstan/', RedirectView.as_view(url=reverse_lazy('kazakhstan'), permanent=True)),
    path('tradeinn/', TradeinnPageView.as_view(), name='trade_inn'),
    path('trade_inn/', RedirectView.as_view(url=reverse_lazy('trade_inn'), permanent=True)),
    path('about/', AboutUsPageView.as_view(), name='about_us'),
    path('contacts/', ContactsPageView.as_view(), name='contacts'),
    path('tariff/', TariffsPageView.as_view(), name='tariffs'),
    path('tariffs/', RedirectView.as_view(url=reverse_lazy('tariffs'), permanent=True)),
    path('create_order/', AloneUnregPageView.as_view(), name='order-alone-page'),
    path('vinyl/', VinilPageView.as_view(), name='vinyl'),

    path('shops/', ShopListView.as_view(), name='shops'),

    path('lk/', LkHelloPageView.as_view(), name='lk-start'),
    path('lk/create_order/', LkCreateOrderPageView.as_view(), name='lk-create-order'),
    path('lk/orders/', LkOrdersPageView.as_view(), name='lk-orders'),
    path('lk/order/<int:order_id>',LkOrderPageView.as_view(), name='lk-order'),
    path('lk/preorders/', LkPreordersPageView.as_view(), name='lk-pre-orders'),
    path('lk/delete_preorder/',LkPreordersDeletePageView.as_view(), name='lk-delete-preorder'),
    path('lk/profile/', LkProfilePageView.as_view(), name='lk-profile'),
    path('lk/messages/', LkMessagesPageView.as_view(), name='lk-messages'),
    path('lk/logout/', LkLogoutPageView.as_view(), name='lk-logout')
]