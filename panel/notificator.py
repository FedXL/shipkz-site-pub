import datetime
from typing import Dict

import redis
from django.conf import settings

from app_bot.management.bot_core import sync_bot
from app_front.management.email.email_sender import my_logger
from legacy.models import Orders, Messages, Users, WebUsers, WebMessages


def text_status_generator(order: Orders, status: str) -> tuple[str, tuple[int, str]]:
    order_id = order.id
    row = order.group
    data = row.to_dict()
    host_county = row.buyer.country
    if host_county == 'KAZAKHSTAN':
        host_county = 'Казахстан'
    elif host_county == 'KYRGYZSTAN':
        host_county = 'Кыргызстан'
    buyer_text = None
    match status:
        case "paid":
            user_text = f"Ваш заказ выкуплен в магазине. Номер заказа: {order_id}. Магазин: {data.get('shop', None)}."
        case "arrived_to_forward":
            user_text = f"Ваш заказ прибыл на склад форвардера. Номер заказа: {order_id}."
        case "got_track":
            user_text = (f"Ваш заказ отправлен в {host_county}. Номер заказа: {order_id}."
                         f" Трек: {data.get('trek',None)}. Почтовый сервис: {data.get('post_service', None)}.")
            buyer_text = (f"Заказ отправлен в {host_county}. Трек: {data.get('trek', None)}."
                          f"Почтовый сервис: {data.get('post_service')}. Вознаграждение составит: {data.get('buyer_reward')}.")
        case "arrived_to_host_country":
            user_text = f"Ваш заказ прибыл на территорию {host_county}. Номер заказа: {order_id}."
            buyer_text = (f"Лови посылку. Заказ уже в {host_county}. Трек: {data.get('trek',None)}. "
                          f"Почтовый сервис: {data['post_service']}. Вознаграждение составит: {data['buyer_reward']}.")
        case "received_in_host_country":
            user_text = f"Ваш заказ получен в {host_county}е. Номер заказа: {order_id}."
            buyer_text = f"Отлично. Особые инструкции:  {data.get('buyer_instructions')}"
        case "send_to_ru":
            cdek = order.ori.cdek
            user_text = f"Ваш заказ отправлен в Россию. Номер заказа: {order_id}. Номер СДЕК: {cdek}."
        case "success":
            user_text = (f"Мы рады, что вы получили заказ: {order_id}. Подарите нам видео распаковки"
                         f" посылки, и получите скидку 1000 руб. на следующий заказ. Отзыв можно оставить в чате нашего"
                         f" телеграмм-канала @shipkz_discussing.")
        case _:
            return False, False
    for_buyer_send = (
        data['buyer'], buyer_text)
    return user_text, for_buyer_send


class Notificator:
    def __init__(self, order: Orders, status: str):
        self.order = order
        self.status = status

    def __get_user(self,order: Orders) -> Dict[str, Users] | Dict[str, WebUsers]:
        telegram_user = order.client
        web_user = order.web_user
        if telegram_user:
            return {'telegram': telegram_user}
        elif web_user:
            return {'web': web_user}

    def __check_profile(self) -> dict:
        """Проверка наличия профиля у пользователя
        Если есть, то возвращает словарь с ключом 'telegram' или 'web'
        Если нет, то возвращает словарь с ключом 'telegram' или 'web' и значением False
        user_dict = {'telegram': telegram_user,'web': web_user}
        """
        order = self.order
        user_dict = self.__get_user(order)
        if user_dict.get('telegram'):
            tele_user:Users = user_dict.get('telegram')
            profile = tele_user.profile.first()
            if profile:
                web_user = profile.web_user
                if web_user:
                    user_dict['web'] = web_user
        elif user_dict.get('web'):
            web_user = user_dict.get('web')
            profile = web_user.profile.first()
            if profile:
                tele_user = profile.telegram_user
                if tele_user:
                    user_dict['telegram'] = tele_user
        else:
            raise ValueError('No user found')
        return user_dict

    def __get_text_for_client(self) -> tuple[str, tuple[int, str]]:
        return text_status_generator(self.order, self.status)

    def __save__telegram_message(self,text:str,telegram_user_obj:Users):
        message = Messages.objects.create(storage=telegram_user_obj,
                                              message_body=text,
                                              is_answer=False)
        message.save()
        return True, message

    def __save_web_message(self,text,web_user_obj):
        message = WebMessages.objects.create(user=web_user_obj,
                                                 message_body=text,
                                                 is_answer=False,
                                                 message_type='text',
                                                 is_read=False)
        message.save()
        return True, message


    def __send_redis_mess_to_web(self, message_id,
                                 user_id,
                                 text):

        data_dict = self.__serializer_for_redis_pubsub(message_id=message_id,
                                                       user_id=user_id,
                                                       text=text)
        channel = 'news'
        data = str(data_dict)
        redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        redis_client.pubsub()
        redis_client.publish(channel, data)
        return True, data_dict


    def __serializer_for_redis_pubsub(self, message_id: int, user_id: int, text: str):
        now = datetime.datetime.now()
        formatted_datetime = now.strftime("%B %d, %H:%M")
        data = {
            'event': 'message',
            'name': 'Askar',
            'details': {'message_id': message_id,
                        'is_answer': True,
                        'user_id': user_id,
                        'message_type': 'text',
                        'time': formatted_datetime,
                        'text': text,
                        'user_name': 'Askar',
                        'is_read': False}
        }
        return data

    def send_notification(self) -> {'telegram': bool, 'web': bool}:
        user_text, buyer_text = self.__get_text_for_client()
        send_result = {}

        if user_text:
            user_dict = self.__check_profile()
            my_logger.info(user_dict)
            if user_dict.get('telegram'):
                telegram_user_obj = user_dict.get('telegram')
                result, telegram_message = self.__save__telegram_message(text=user_text,telegram_user_obj=telegram_user_obj)
                message = sync_bot.send_message(chat_id=telegram_user_obj.user_id,text=user_text)
                if message:
                    send_result['telegram']=True
                else:
                    send_result['telegram'] = False
            else:
                send_result['telegram'] = False
            if user_dict.get('web'):
                user_id = user_dict.get('web')
                result, web_message = self.__save_web_message(text=user_text,web_user_obj=user_id)
                result, web_message=self.__send_redis_mess_to_web(message_id = web_message.id,user_id=user_id,text=user_text)
                send_result['web']=True
            else:
                send_result['web'] = False
        else:
            send_result['telegram'] = False
            send_result['web'] = False
        return send_result







