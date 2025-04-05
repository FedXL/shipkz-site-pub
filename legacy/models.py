import datetime
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from panel.models import OrdersGroup


class WebUsers(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=255, blank=True, null=True) # FIXME: не используется надо бы удалить
    web_username = models.CharField(unique=True, max_length=255, blank=True, null=True)
    is_kazakhstan = models.BooleanField(blank=True, null=True, default=True)
    last_online = models.DateTimeField(blank=True, null=True)
    last_message_telegramm_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'web_users'

    def get_chat_id(self):
        if self.is_kazakhstan:
            chat_id = settings.KAZAKHSTAN_CATCH_CHAT
        else:
            chat_id = settings.TRADEINN_CATCH_CHAT
        return chat_id

    def __str__ (self):
        return f"{self.web_username}-{self.user_id}"

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'web_username': self.web_username,
            'is_kazakhstan': self.is_kazakhstan,
            'last_online': self.last_online,
            'last_message_telegramm_id': self.last_message_telegramm_id
        }

class Users(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    user_name = models.CharField(max_length=255, blank=True, null=True)
    message_id = models.IntegerField(blank=True, null=True)
    tele_username = models.CharField(max_length=50, blank=True, null=True)
    user_second_name = models.CharField(max_length=50, blank=True, null=True)
    main_user = models.IntegerField(blank=True, null=True)
    is_kazakhstan = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'
        verbose_name = 'Телеграм пользователь'

    def __str__(self):
        return f"{self.user_id}-{self.user_name}"

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'message_id': self.message_id,
            'tele_username': self.tele_username,
            'user_second_name': self.user_second_name,
            'main_user': self.main_user,
            'is_kazakhstan': self.is_kazakhstan
        }


class Buyers(models.Model):
    COUNTRY_CHOICES = [
        ('KAZAKHSTAN', 'KAZAKHSTAN'),
        ('KYRGYZSTAN', 'KYRGYZSTAN'),
    ]

    country = models.CharField(
        max_length=255,
        choices=COUNTRY_CHOICES,
        blank=True,
        null=True,
        verbose_name='Страна'
    )

    phone = models.BigIntegerField(blank=True, null=True)
    telegram_id = models.BigIntegerField(blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    second_name = models.CharField(max_length=50, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'buyers'

    def __str__(self):
        return self.first_name

    def to_dict(self):
        return {
            'country': self.country,
            'phone': self.phone,
            'telegram_id': self.telegram_id,
            'first_name': self.first_name,
            'second_name': self.second_name,
            'comments': self.comments
        }

class Discounts(models.Model):
    is_vip = models.BooleanField(blank=True, null=True)
    user = models.OneToOneField('Users', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'discounts'


class Documents(models.Model):
    document_id = models.TextField(blank=True, null=True)
    message = models.ForeignKey('Messages', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'documents'


class EmailTask(models.Model):
    web_user = models.ForeignKey('WebUsers', models.DO_NOTHING, db_column='web_user')
    text = models.TextField()
    header = models.CharField(max_length=255)
    execute_time = models.DateTimeField()
    status = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'email_task'


class Exchange(models.Model):
    valuta = models.CharField(primary_key=True, max_length=10)
    price = models.FloatField(blank=True, null=True)
    data = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'exchange'


class FastAnswers(models.Model):
    body = models.TextField(blank=True, null=True)
    button_name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    manager = models.ForeignKey('Managers', models.DO_NOTHING, db_column='manager', to_field='user_id', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fast_answers'


class Jwt(models.Model):
    user = models.OneToOneField('WebUsers', models.DO_NOTHING, blank=True, null=True)
    jwt_hash = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jwt'


class Managers(models.Model):
    short_name = models.CharField(max_length=255, blank=True, null=True)
    user = models.OneToOneField(Users, models.DO_NOTHING, blank=True, null=True)
    key = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'managers'

    def __str__(self):
        return self.short_name


class Messages(models.Model):
    message_body = models.TextField(blank=True, null=True)
    is_answer = models.BooleanField(blank=True, null=True)
    storage = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    message_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'messages'


class Orders(models.Model):
    TYPE_CHOICES = [
        ('TRADEINN','TRADEINN'),
        ('KAZ_ORDER_LINKS','KAZ_ORDER_LINKS'),
        ('WEB_ORDER','WEB_ORDER'),
        ('PAYMENT','PAYMENT')
    ]


    client = models.ForeignKey(Users, models.DO_NOTHING, db_column='client', blank=True, null=True)
    buyer = models.ForeignKey(Buyers, models.DO_NOTHING, db_column='buyer', blank=True, null=True)
    type = models.CharField(choices=TYPE_CHOICES,max_length=255, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    web_user = models.ForeignKey(WebUsers, models.DO_NOTHING, db_column='web_user', blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    user_ip = models.CharField(max_length=100, blank=True, null=True)
    group = models.ForeignKey(OrdersGroup, models.DO_NOTHING, blank=True, null=True,related_name='orders')

    def clean(self):
        if not self.client and not self.web_user:
            raise ValidationError('Either client or web_user must be filled.')

    class Meta:
        managed = False
        db_table = 'orders'

    def to_dict(self,dict_variant=None):
        result = {
            'order_id': self.id,
            'order_link': f"/admin/legacy/orders/{self.id}/change/",
            'buyer': self.buyer,
            'order_type': self.type,
            'order_body': self.body,
            'order_date': self.time,
            'order_status': self.status,
            'order_user_ip': self.user_ip
        }

        if self.client:
            result['client'] = self.client.user_name
            result['client_link'] = f'/panel/client-profile/?client_type=telegram&client_id={self.client.user_id}'
            result['client_hint'] = 'tel'

        if self.web_user:
            result['client'] = self.web_user.web_username
            result['client_link'] = f'/panel/client-profile/?client_type=web&client_id={self.web_user.user_id}'
            result['client_hint'] = 'web'

        if OrderStatusInfo.objects.filter(order=self).exists():
            order_status_info = OrderStatusInfo.objects.get(order=self)
            order_status_info_dict= order_status_info.to_dict()
            result = {**result, **order_status_info_dict}

        if OrderStatus.objects.filter(order=self).exists():
            order_status = OrderStatus.objects.get(order=self)
            order_status_dict = order_status.to_dict()
            result = {**result, **order_status_dict}
        return result

    def __repr__(self):
        return f'Order {self.id} / {self.client} / {self.web_user}'

    def __str__(self):
        return f"{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(to=Orders, on_delete=models.CASCADE, blank=True, null=True,related_name='order_items')
    url = models.URLField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    price = models.CharField(max_length=255, blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)

class OrderStatus(models.Model):
    status = models.BooleanField(blank=True, null=True)
    order_price = models.CharField(max_length=255, blank=True, null=True)
    order = models.ForeignKey(Orders, models.DO_NOTHING, related_name='ori_tradeinn', blank=True, null=True)
    manager = models.ForeignKey(Managers, models.DO_NOTHING, to_field='user_id', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_status'
        verbose_name = 'Tradeinn Информация о заказе'

    def to_dict(self):
        return {
            'status': self.status,
            'order_price': self.order_price,
            'manager': self.manager
        }


class OrderStatusInfo(models.Model):
    COUNTRY_CHOICES = [
        ('KAZAKHSTAN', 'KAZAKHSTAN'),
        ('KYRGYZSTAN', 'KYRGYZSTAN'),
    ]

    host_country = models.CharField(
        max_length=255,
        choices=COUNTRY_CHOICES,
        blank=True,
        null=True,
        verbose_name='Страна назначения'
    )

    order = models.OneToOneField(Orders, models.DO_NOTHING, related_name='ori')
    paid = models.DateTimeField(default=datetime.datetime(2024, 1, 1))
    arrived_to_forward = models.DateTimeField(blank=True, null=True)
    got_track = models.DateTimeField(blank=True, null=True)

    arrived_to_host_country = models.DateTimeField(blank=True, null=True)
    received_in_host_country = models.DateTimeField(blank=True, null=True)

    send_to_ru = models.DateTimeField(blank=True, null=True)
    success = models.DateTimeField(blank=True, null=True, verbose_name='Дата получения посылки')

    relative_price = models.CharField(max_length=255, blank=True, null=True)
    is_forward = models.BooleanField(default=False, verbose_name="Заказ через форвардера")

    buyer_reward = models.CharField(max_length=255, blank=True, null=True)
    shop = models.CharField(max_length=255,blank=True, null=True)
    order_sum = models.CharField(max_length=255, blank=True, null=True)
    order_currency = models.CharField(max_length=255, blank=True, null=True)
    store_order_number = models.CharField(max_length=255,blank=True, null=True)
    buyer = models.IntegerField(blank=True, null=True)
    buyer_telegram = models.ForeignKey(Buyers, models.DO_NOTHING,db_column='buyer_telegram', related_name='ori_buyer', blank=True, null=True)
    forward_name = models.CharField(max_length=255, null=True, blank=True)
    post_service = models.CharField(max_length=50, blank=True, null=True,verbose_name='Почтовая служба')
    trek = models.CharField(max_length=255, blank=True, null=True)
    estimated_date_of_arrival = models.CharField(max_length=255, blank=True, null=True,verbose_name='Ориентировочная дата прибытия КЗ')
    cdek = models.CharField(max_length=255, blank=True, null=True)
    payment_card = models.CharField(max_length=255, blank=True, null=True,verbose_name='Карта для оплаты')
    is_delivery_payment = models.BooleanField(default=False,verbose_name="Оплачена ли доставка в РФ")
    comment = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_status_info'
        verbose_name = 'Транзит информация о заказе'
        verbose_name_plural = 'Транзит информация о заказах'

    def to_dict(self):


        result = {
            'is_forward': self.is_forward,
            'host_country': self.host_country,
            'paid': self.paid,
            'arrived_to_forward': self.arrived_to_forward,
            'got_track': self.got_track,
            'arrived_to_host_country': self.arrived_to_host_country,
            'received_in_host_country': self.received_in_host_country,
            'send_to_ru': self.send_to_ru,
            'success': self.success,
            'relative_price': self.relative_price,
            'buyer_reward': self.buyer_reward,
            'shop': self.shop,
            'order_sum': self.order_sum,
            'order_currency': self.order_currency,
            'store_order_number': self.store_order_number,
            'buyer': self.buyer,
            'forward_name': self.forward_name,
            'post_service': self.post_service,
            'trek': self.trek,
            'estimated_date_of_arrival': self.estimated_date_of_arrival,
            'cdek': self.cdek,
            'payment_card': self.payment_card,
            'is_delivery_payment': self.is_delivery_payment,
            'comment': self.comment
        }
        return result

class ParceTask(models.Model):
    order = models.ForeignKey(Orders, models.DO_NOTHING, blank=True, null=True)
    login = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'parce_task'


class Photos(models.Model):
    photo_id = models.AutoField(primary_key=True)
    file_id = models.TextField(blank=True, null=True)
    message = models.ForeignKey(Messages, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'photos'


class Posts(models.Model):
    id = models.BigAutoField(primary_key=True)
    message_id = models.BigIntegerField(blank=True, null=True)
    chat_id = models.BigIntegerField(blank=True, null=True)
    name = models.CharField(unique=True, max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'posts'

class Services(models.Model):
    service_name = models.CharField(primary_key=True, max_length=255)
    status = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    report = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'services'



class UsersApp(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=250)

    class Meta:
        managed = False
        db_table = 'users_app'

class WebDocs(models.Model):
    doc_path = models.CharField(max_length=255, blank=True, null=True)
    message = models.ForeignKey('WebMessages', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'web_docs'




class WebMessages(models.Model):
    id = models.BigAutoField(primary_key=True)
    message_body = models.TextField(blank=True, null=True)
    is_answer = models.BooleanField(blank=True, null=True)
    user = models.ForeignKey(WebUsers, models.DO_NOTHING, db_column='user')
    time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    message_type = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'web_messages'

    def as_dict(self):
        result = {'message_id': self.id,
                  'text': self.message_body,
                  'is_answer': self.is_answer,
                  'user_id': self.user.user_id,
                  'time': self.time.strftime("%B %d, %H:%M"),
                  'message_type': self.message_type,
                  'is_read': self.is_read
                  }
        return result


class WebPhotos(models.Model):
    photo_path = models.CharField(max_length=255, blank=True, null=True)
    message = models.ForeignKey(WebMessages, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'web_photos'


class WebUsersMeta(models.Model):
    meta_id = models.AutoField(primary_key=True)
    field = models.CharField(max_length=255)
    value = models.CharField(max_length=255, blank=True, null=True)
    web_user = models.ForeignKey(WebUsers, models.DO_NOTHING, db_column='web_user',related_name='user_meta')

    class Meta:
        managed = False
        db_table = 'web_users_meta'
        unique_together = (('field', 'web_user'),)

    def to_dict(self):
        return {
            'meta_id': self.meta_id,
            'field': self.field,
            'value': self.value,
            'web_user': self.web_user
        }



class Websockets(models.Model):
    id = models.BigAutoField(primary_key=True)
    socket_id = models.BigIntegerField(blank=True, null=True)
    user = models.OneToOneField(WebUsers, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'websockets'


class WebsocketsSupport(models.Model):
    socket_id = models.BigIntegerField(blank=True, null=True)
    user = models.OneToOneField(WebUsers, models.DO_NOTHING, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'websockets_support'

class RootUsers(models.Model):
    telegram_user = models.ForeignKey(Users, models.DO_NOTHING, db_column='telegram_user', blank=True, null=True)
    web_user = models.ForeignKey(WebUsers, models.DO_NOTHING, db_column='web_user', blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'root_users'


