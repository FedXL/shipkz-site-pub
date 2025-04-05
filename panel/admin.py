from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin
from panel.models import OrdersGroup
from legacy.models import Orders

@admin.register(OrdersGroup)
class OrdersGroupAdmin(admin.ModelAdmin):

    list_display = ['id','view_orders','group_name',
                    'order_date',
                    'buyer_reward',
                    'shop',
                    'order_sum',
                    'order_currency',
                    'store_order_number',
                    'buyer',
                    'is_forward',
                    'forward_name',
                    'post_service',
                    'trek',
                    'estimated_date_of_arrival',
                    'payment_card',
                    'is_delivery_payment','comment']
    search_fields = ['id','group_name']

    def view_orders(self, obj):
        orders = Orders.objects.filter(group=obj)
        if not orders.exists():
            return "No related orders."
        links = [
            format_html(
                '<a href="{}">Order {}</a>',
                reverse('admin:legacy_orders_change', args=[order.id]),
                order.id
            )
            for order in orders
        ]
        return format_html('<br>'.join(links))
    view_orders.short_description = 'Related Orders'


