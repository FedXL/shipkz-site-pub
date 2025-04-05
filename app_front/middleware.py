import traceback
from django.conf import settings
from django.http import JsonResponse
from django.middleware.csrf import CsrfViewMiddleware
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from app_bot.management.bot_core import sync_bot
from app_front.management.email.email_sender import my_logger
from app_front.management.unregister_authorization.token import check_token, create_token
from app_front.management.unregister_authorization.unregister_web_users import generate_random_name
from app_front.management.utils import get_user_ip
from legacy.models import WebUsers

class UnregisterAuthMiddleware:
    token = ''
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.session.exists(request.session.session_key):
            response = self.get_response(request)
            return response

        token = request.COOKIES.get('ShipKZAuthorization')
        if not token:
            self.handle_no_token(request)
        else:
            self.handle_token(request, token)

        response = self.get_response(request)
        response.set_cookie('ShipKZAuthorization', self.token, max_age=60*60*24*14)
        return response

    def handle_no_token(self, request):
        new_username = generate_random_name()
        new_username = 'UNREG_' + new_username
        web_user = WebUsers.objects.create(web_username=new_username)
        user_ip = get_user_ip(request)
        new_token = create_token(username=new_username,
                                 user_id=web_user.user_id,
                                 ip=user_ip)
        self.token = new_token

    def handle_token(self, request, token):
        decoded_token = check_token(token)
        if decoded_token:
            self.token = token
        else:
            self.handle_no_token(request)


class RemoveCORSHeadersForYandexMetrikaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        referer = request.META.get('HTTP_REFERER', '')

        if "metrika.yandex.ru" in referer:
            # Удаляем заголовки, если запрос с Яндекс.Метрики
            if 'Cross-Origin-Opener-Policy' in response:
                del response['Cross-Origin-Opener-Policy']
            if 'Cross-Origin-Resource-Policy' in response:
                del response['Cross-Origin-Resource-Policy']
        return response


class CustomCsrfMiddleware(CsrfViewMiddleware):
    def _reject(self, request, reason):
        """Перехватываем ошибку CSRF и отправляем в Telegram"""
        user_id = request.user.id if request.user.is_authenticated else "Anonymous"
        user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")
        IP = get_user_ip(request)

        # 🔹 Логируем CSRF-токены
        csrf_cookie = request.COOKIES.get('csrftoken', 'Пустой')
        csrf_header = request.headers.get('X-CSRFToken', 'Пустой')

        my_logger.error(f"⚠️ CSRF ERROR for user {user_id}: {reason}")
        my_logger.error(f"🌐 IP: {IP}")
        my_logger.error(f"🖥 User-Agent: {user_agent}")
        my_logger.error(f"🔗 Path: {request.path}, Method: {request.method}")
        my_logger.error(f"🔒 CSRF-Token из Cookie: {csrf_cookie}")
        my_logger.error(f"📩 CSRF-Token из Headers: {csrf_header}")

        message = (
            f"<b>⚠ CSRF Error Detected ⚠</b>\n"
            f"<b>🔗 Path:</b> {request.path}\n"
            f"<b>🛠 Method:</b> {request.method}\n"
            f"<b>🙍 User ID:</b> {user_id}\n"
            f"<b>🖥 Browser:</b> {user_agent}\n"
            f"<b>💥 CSRF Error:</b> {reason}\n"
            f"<b>🌐 IP:</b> {IP}\n"
            f"<b>🔒 CSRF-Token из Cookie:</b> {csrf_cookie}\n"
            f"<b>📩 CSRF-Token из Headers:</b> {csrf_header}"
        )
        try:
            sync_bot.send_message(chat_id=settings.ORDERS_CATCH_CHAT, text=message)
        except Exception as e:
            my_logger.error(f"❌ Failed to send CSRF error to Telegram: {e}")
        return render(request, "pages/csrf-error.html", status=403)




class ExceptionHandlingMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        # Формируем сообщение для Telegram
        message = (
            f"<b>Error in Application:</b>\n"
            f"<b>Path:</b> {request.path}\n"
            f"<b>Method:</b> {request.method}\n"
            f"<b>Exception:</b> {exception.__class__.__name__}\n"
            f"<b>Message:</b> {str(exception)}\n\n"
            f"<b>Traceback:</b>\n<pre>{traceback.format_exc()}</pre>"
        )
        try:
            sync_bot.send_message(chat_id=settings.ORDERS_CATCH_CHAT, text=message)
        except Exception as e:
            print(f"Failed to send error message to Telegram: {e}")
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)