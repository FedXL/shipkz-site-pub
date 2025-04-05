import json
from typing import Tuple
from celery import shared_task
from django.conf import settings
from app_auth.models import Profile
from app_bot.management.bot_core import sync_bot, web_open_meeting_message_in_bot
from app_front.management.email.email_sender import send_email, send_order_notification_email, \
    send_register_order_notification_email, my_logger
from app_front.management.google_sheets.sheets_handlers import  add_last_string33
from legacy.models import WebUsersMeta, Orders, WebUsers, WebMessages


def create_unregister_web_order(data,web_user_id,user_ip) ->Tuple[Orders,WebUsers]:
    """data = form data from unregistered order form fields {url, price, count, comment, email, phone}"""

    url = data.get('url')
    price = data.get('price')
    count = data.get('count')
    comment = data.get('comment')
    email = data.get('email')
    phone = data.get('phone')
    web_user = WebUsers.objects.get(user_id=web_user_id)

    user_email, created_email = WebUsersMeta.objects.update_or_create(
        web_user=web_user,
        field='email',
        defaults={'value': email}
    )

    user_phone, created_phone = WebUsersMeta.objects.update_or_create(
        web_user=web_user,
        field='phone',
        defaults={'value': phone}
    )

    order = Orders.objects.create(
        type='WEB_ORDER',
        body=json.dumps(data),
        user_ip=user_ip,
        web_user=web_user
    )
    return order, web_user


def create_text_from_unreg_body(data):
    """

{"country": "EUROPE",
 "url": "https://www.xspo.com/rossignol-hero-world-cup-kit-lifters-srews-3mm--",
  "price": "100",
  "count": 1,
  "comment": "",
   "email": "askarduisekulov@yandex.ru",
    "phone": "\u043c\u043e\u0438\u043b\u0438\u043b\u0438\u043b\u043e",
     "captcha": ["6ed9b18419e2d64bc0fe6d312de47b7050b6b04f", ""]}

    :param body:
    :return:
    """
    country = data.get('country')
    url = data.get('url')
    price = data.get('price')
    count = data.get('count')
    comment = data.get('comment')
    email = data.get('email')
    phone = data.get('phone')

    text = f"Страна: <code>{country}</code>\n"

    text += f'<a href="{url}">Link</a>\n'
    text += f"Ценa: <code>{price}</code>\n"
    text += f"Количество: <code>{count}</code>\n"
    text += f"Комментарий: <code>{comment}</code>\n"
    text += f"Email: <code>{email}</code>\n"
    text += f"Телефон: <code> {phone}</code>\n"
    text += "\n"
    text += f"Url(запасной): <code>{url} </code>\n"

    return text



@shared_task
def unregister_web_task_way(data:dict,
                            web_user_id:str,
                            user_ip:str):
    """История про ордеры"""
    email = data.get('email')
    order, web_user = create_unregister_web_order(data, web_user_id, user_ip)
    message_body = f"/order_{order.id}"
    web_message = WebMessages.objects.create(message_body=message_body,
                                                user=web_user,
                                                is_answer=False,
                                                message_type='order',
                                                is_read=True)

    send_order_notification_email(to_mail=email, form_data=data, order_number=order.id)
    send_order_notification_email(to_mail='shipkz.ru@gmail.com', form_data=data, order_number=order.id,is_self_mail=email)

    text = "Незарегистрированный пользователь\n"
    text += web_user.web_username
    text += "\n"
    text += f"Заказ-{order.id}\n"
    text += '\n'
    try:
        text += create_text_from_unreg_body(data)
    except Exception as e:
        my_logger.error(f'Error in create_text_from_unreg_body {e}')
        text += str(order.body)
        text += f"\n"
    text += "[META]\n"
    meta = WebUsersMeta.objects.filter(web_user=web_user)
    for row in meta:
        text += f"{row.field}: {row.value}\n"
    sync_bot.send_message(chat_id=settings.ORDERS_CATCH_CHAT, text=text)
    web_open_meeting_message_in_bot(web_user)
    add_last_string33(values=[(f'{order.id}', f'{web_user.web_username}', f'{order.body}')], sheet='Dashboard')
    return 'Success unregister web task way'


@shared_task()
def registered_web_task_way(order_id):
    order = Orders.objects.get(id=order_id)
    web_user = order.web_user
    data = json.loads(order.body)

    profile = Profile.objects.filter(web_user=web_user).first()
    email = profile.email
    send_register_order_notification_email(to_mail=email,
                                           username=web_user.web_username,
                                           order_number=order.id,
                                           country=data.get('country'),
                                           goods=data.get('items'),)

    send_register_order_notification_email(to_mail='shipkz.ru@gmail.com',
                                           username=web_user.web_username,
                                           order_number=order.id,
                                           country=data.get('country'),
                                           goods=data.get('items'),
                                           is_self_mail=email)
    text = ""
    text += f"#{order.id} \n"
    text += f"Type: Web Order (reg)\n"
    text += f"User: {web_user.web_username}"
    text += "\n"
    goods = data.get('items')
    for num, item in goods.items():
        text += f'<a href="{item.get("url")}">линк-{num}</a>\n'
        text += f"{item.get('amount')}\n"
        text += f"{item.get('comment')}\n"
    text += f"\n"
    text += "[META]\n"
    meta = WebUsersMeta.objects.filter(web_user=web_user)
    for row in meta:
        text += f"{row.field}: {row.value}\n"

    sync_bot.send_message(chat_id=settings.ORDERS_CATCH_CHAT, text=text)
    new_web_message = WebMessages.objects.create(message_body=f"/order_{order.id}",
                                                 user=web_user,
                                                 is_answer=False,
                                                 message_type='order',
                                                 is_read=True)
    web_open_meeting_message_in_bot(web_user)
    add_last_string33(values=[(f'{order.id}', f'{web_user.web_username}', f'{order.body}')], sheet='Dashboard')
    return 'Success registered web task way'


