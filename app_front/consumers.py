import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.conf import settings
from app_front.management.unregister_authorization.token import check_token
from legacy.models import WebMessages, WebUsers
from asgiref.sync import sync_to_async

cons_logger = logging.getLogger('CONSUMER LOGGER ')
cons_logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
cons_logger.addHandler(console_handler)

@sync_to_async
def get_web_user_id(user):
    return user.profile.web_user_id

class SupportConsumer(AsyncWebsocketConsumer):
    user_id = ''
    async def connect(self):
        cons_logger.info(f"START CONSUMER!: {self.scope}")
        user = self.scope["user"]
        channel_layer = get_channel_layer()
        if user.is_authenticated:
            cons_logger.info(f"Authenticated User: {user.username}")
            web_user_id = await get_web_user_id(user)
            self.user_id = web_user_id
            await self.save_channel_in_redis(user_id=web_user_id,
                                             channel_name=self.channel_name)
            await self.accept()
            count = await sync_to_async(WebMessages.objects.filter(user_id=web_user_id, is_read=False).count)()
            await self.send(text_data=json.dumps({"message": f"У вас {count} новых сообщений",
                                                  "message_type":"update_counter",
                                                  "count":count}))
        else:
            cons_logger.info("Anonymous User connected")
            cookie_token = self.scope['cookies'].get('ShipKZAuthorization', None)
            if not cookie_token:
                cons_logger.error("No token in scope")
                await self.close()
                return
            await self.accept()
            decrypted_token = check_token(cookie_token)

            if not decrypted_token:
                cons_logger.error("Invalid token")
                await self.close()
                return

            username = decrypted_token.get('username')
            web_user = await sync_to_async(WebUsers.objects.filter(web_username=username).first)()

            if not web_user:
                cons_logger.error(f"User {username} not found")
                await self.close()
                return
            await self.save_channel_in_redis(web_user.user_id, self.channel_name)
            count = await sync_to_async(WebMessages.objects.filter(user_id=web_user.user_id, is_read=False).count)()
            await self.send(text_data=json.dumps({"message": f"У вас {count} новых сообщений",
                                                  "message_type":"update_counter",
                                                  "count":count}))

    async def send_message_counter(self, event):
        print('yo')
        cons_logger.warning(f"Start trigger foo unread counter: ")
        """отправить в меню количество непрочитанных сообщений"""
        message_data = event['message_data']
        counter = message_data.get('count', None)
        if not counter:
            cons_logger.error("No counter in message data")
            return
        data = {"message_type": "update_counter","count":counter}
        cons_logger.info(f"Send message to support: {data}")
        await self.send(json.dumps(data))


    async def save_channel_in_redis(self, user_id, channel_name):
        await sync_to_async(self.set_redis_channel)(user_id, channel_name)

    async def delete_channel_from_redis(self, user_id):
        await sync_to_async(self.delete_redis_channel)(user_id)

    def set_redis_channel(self, user_id, channel_name):
        redis_client = settings.REDIS_CONNECTION
        redis_client.set(f"ws_user_id_{user_id}", channel_name)

    def delete_redis_channel(self, user_id):
        redis_client = settings.REDIS_CONNECTION
        redis_client.delete(f"ws_user_id_{user_id}")

    async def disconnect(self, close_code):
        cons_logger.info(f"Disconnected: {self.user_id}")
        if hasattr(self, 'channel_group_name'):
            await self.channel_layer.group_discard(self.channel_group_name, self.channel_name)
            await self.delete_channel_from_redis(self.scope['user'].id)