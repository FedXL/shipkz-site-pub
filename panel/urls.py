from django.urls import path
from panel.views import OrdersTransitView, OrdersTradeinnView, BayersView, OrdersStatisticView, EditOrderInfoView, \
    ProfileView

urlpatterns = [
    path('orders-transit/', OrdersTransitView.as_view(), name='orders-transit'),
    path('orders-tradeinn/', OrdersTradeinnView.as_view(), name='orders-tradeinn'),
    path('buyers/', BayersView.as_view(), name='buyers'),
    path('orders-statistic/', OrdersStatisticView.as_view(),name='orders-statistic'),
    path('row-edit/', EditOrderInfoView.as_view(), name='row-edit'),
    path('client-profile/',ProfileView.as_view(),name='client-profile'),
   ]