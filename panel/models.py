from django.db import models



class OrdersGroup(models.Model):
     group_name = models.CharField(max_length=255, blank=True, null=True)

     order_date = models.DateField(blank=True, null=True, verbose_name='Дата заказа')
     buyer_reward = models.CharField(max_length=255, blank=True, null=True, verbose_name='Вознаграждение баера')
     shop = models.CharField(max_length=255, blank=True, null=True, verbose_name='Магазин')
     order_sum = models.CharField(max_length=255, blank=True, null=True, verbose_name='Сумма заказа')
     order_currency = models.CharField(max_length=255, blank=True, null=True, verbose_name='Валюта')
     store_order_number = models.CharField(max_length=255, blank=True, null=True,verbose_name='Номер заказа в магазине/номер заказа у Форвардера')
     buyer = models.ForeignKey('legacy.Buyers', models.DO_NOTHING, related_name='row_buyer',
                               blank=True, null=True, verbose_name='Байер')
     is_forward = models.BooleanField(default=False, verbose_name="True если заказ через форвардера")
     forward_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Форвардер название')
     post_service = models.CharField(max_length=50, blank=True, null=True, verbose_name='Почтовая служба')
     trek = models.CharField(max_length=255, blank=True, null=True, verbose_name='Трек')
     estimated_date_of_arrival = models.CharField(max_length=255, blank=True, null=True,
                                                  verbose_name='Ориентировочная дата прибытия КЗ')
     payment_card = models.CharField(max_length=255, blank=True, null=True, verbose_name='Карта для оплаты')
     is_delivery_payment = models.BooleanField(default=False, verbose_name="Оплачена ли доставка в РФ")
     comment = models.CharField(blank=True, null=True)

     def to_dict(self):
          result = {
               'buyer_reward': self.buyer_reward,
               'shop': self.shop,
               'order_sum': self.order_sum,
               'order_currency': self.order_currency,
               'order_date': self.order_date,
               'store_order_number': self.store_order_number,
               'buyer': self.buyer,
               'is_forward': self.is_forward,
               'forward_name': self.forward_name,
               'post_service': self.post_service,
               'trek': self.trek,
               'estimated_date_of_arrival': self.estimated_date_of_arrival,
               'payment_card': self.payment_card,
               'is_delivery_payment': self.is_delivery_payment,
               'comment': self.comment
          }
          return result

     def __str__(self):
          return f"{self.id}"

     class Meta:
          verbose_name = 'Информация о заказах'
          verbose_name_plural = 'Информация о заказах'




