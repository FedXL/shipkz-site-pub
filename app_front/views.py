import json
from typing import Tuple
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views import View
from app_auth.forms import ProfileModelForm, CallbackResponseForm
from app_auth.mixins import ActiveUserConfirmMixin
from app_auth.mixins import EmailVerificationRequiredMixin
from app_auth.models import Profile
from app_bot.management.bot_core import sync_bot
from app_front.forms import UnregisteredOrderForm, OrderForm, RegisterOrderItemFormSet
from app_front.management.orders.orders_handler import get_orders_by_username_pre, get_orders_by_username_full, \
    body_parser
from app_front.management.unregister_authorization.token import check_token, handle_no_token_comeback_version, \
    create_access_token
from app_front.management.utils import get_user_ip
from app_front.models import CallbackForm
from legacy.models import Exchange, WebUsers, Orders, WebUsersMeta
from app_front.tasks import unregister_web_task_way, registered_web_task_way
from legacy.serializers import OrderFullSerializer, OrdersSerializerPre
from seo.models import ShopCategory


def sitemap_view(request):
    xml = render_to_string('pages/sitemap.xml', {'now': timezone.now()})
    return HttpResponse(xml, content_type='application/xml')


class TariffsPageView(View):
    def get(self, request):
        eur_obj = Exchange.objects.get(valuta='eur')
        usd_obj = Exchange.objects.get(valuta='usd')
        sber_usd_obj = Exchange.objects.get(valuta='raif_usd')
        sber_euro_obj = Exchange.objects.get(valuta='raif_euro')
        exchange_rates ={'sber_usd': {
                                                    'price': sber_usd_obj.price,
                                                    'data': sber_usd_obj.data
                                                },
                                                'sber_euro': {
                                                    "price": sber_euro_obj.price,
                                                    "data": sber_euro_obj.data
                                                },
                                                'usd': {
                                                    "price": usd_obj.price,
                                                    "data": usd_obj.data
                                                },
                                                'eur': {
                                                    "price": eur_obj.price,
                                                    "data": eur_obj.data
                                                }
                                            }

        json_rates = json.dumps(exchange_rates)
        data = {'exchange_rate': json_rates}
        return render(request,
                      template_name='pages/tariffs.html',
                      context={'data': data})


def auth_cookie_handler (request) -> Tuple[HttpResponse, str, WebUsers,str]:
    """return [response, token, web_user,user_ip] check ShipKzAuthorization cookie and return token and web_user"""
    user_ip = get_user_ip(request)
    token = request.COOKIES.get('ShipKZAuthorization', None)
    decoded_token = check_token(token)
    if decoded_token:
        web_username = decoded_token.get('username')
        web_user = WebUsers.objects.filter(web_username=web_username).first()
    else:
        token, web_user = handle_no_token_comeback_version(user_ip=user_ip)
    response = render(request, template_name='registration/auth_messages.html')
    response.set_cookie('ShipKZAuthorization',
                        token,
                        max_age=14 * 24 * 60 * 60,
                        httponly=False,
                        secure=not settings.DEBUG
                        )
    return response, token, web_user, user_ip


class BaseOrderView(View):
    template_name = ""
    is_start_page = False
    def get(self, request):
        customer = request.user
        if  customer.is_authenticated and customer.email_verified:
            form = OrderForm()
            formset = RegisterOrderItemFormSet()
            pointer = 'registered'
            return render(request, self.template_name, {'form': form, 'formset': formset, 'pointer': pointer,'image_flag':self.is_start_page})
        else:
            pointer = 'unregistered'
            form = UnregisteredOrderForm()
            return render(request, self.template_name, {'form': form, 'pointer': pointer,'image_flag':self.is_start_page})

    def post(self, request):
        customer = request.user
        if customer.is_authenticated and customer.email_verified:
            pointer = 'registered'
            return redirect('lk-create-order')
        else:
            form = UnregisteredOrderForm(request.POST)
            pointer = 'unregistered'
        if form.is_valid():
            data = form.cleaned_data
            form_data = form.cleaned_data
            if pointer == 'unregistered':
                messages.success(request, 'Ваша заявка успешно получена успешно получена')
                messages.success(request, 'В ближайшее время с вами свяжется наш менеджер для уточнения деталей')
                response, token, web_user, user_ip = auth_cookie_handler(request)
                unregister_web_task_way.delay(data=form_data, web_user_id=web_user.user_id, user_ip=user_ip)
                return response
            elif pointer =='registered':
                messages.error(request, 'Как вы сюда попали? Такого быть не должно, что то сломалось.')
                messages.error(request, 'Пожалуйста, обратитесь к администратору')
                redirect('auth_messages')
        else:
            messages.error(request, 'Что-то пошло не так. Проверьте данные и повторите попытку.')
            if pointer == 'unregistered':
                template = 'pages/alone_unreg.html'
            elif pointer == 'registered':
                template = 'lk-pages/lk-create-order-page.html'
            return render(request, template_name=template,context={'form': form,'pointer': pointer})


class AloneUnregPageView(BaseOrderView):
    template_name = 'pages/alone_unreg.html'
    is_start_page = False


class StartingPageView(BaseOrderView):
    template_name = 'pages/start.html'
    is_start_page = True

class KazakhstanPageView(BaseOrderView):
    template_name = 'pages/kazakhstan.html'


class TradeinnPageView(View):
    def get(self, request):
        form = UnregisteredOrderForm()
        return render(request, 'pages/tradeinn.html', {'form': form})

class AboutUsPageView(View):
    def get(self, request):
        return render(request, 'pages/about_us.html')

class ContactsPageView(View):
    def get(self, request):
        return render(request, 'pages/contacts.html')


class LkHelloPageView(ActiveUserConfirmMixin,
                    EmailVerificationRequiredMixin,
                      View):
    def get(self, request):
        return render(request, 'lk-pages/lk-hello-page.html')




class LkCreateOrderPageView(ActiveUserConfirmMixin,EmailVerificationRequiredMixin,View):
    def get(self, request):
        order_form = OrderForm()
        formset = RegisterOrderItemFormSet()
        return render(request, template_name='lk-pages/lk-create-order-page.html',
                      context={
            'form': order_form,
            'formset': formset,
        })

    def post(self, request):
        form = OrderForm(request.POST)
        formset = RegisterOrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            data = form.cleaned_data
            form_set_data = formset.cleaned_data
            user_ip = get_user_ip(request)
            web_user = request.user.profile.web_user
            items_parser_data_for_legacy_bot_agrh = body_parser(form_set_data)
            data['items'] = items_parser_data_for_legacy_bot_agrh
            data = json.dumps(data)
            order = Orders.objects.create(
                type='WEB_ORDER',
                body=data,
                user_ip=user_ip,
                web_user=web_user
            )
            messages.success(request, f'Заявка №{order.id} успешно создана!')
            registered_web_task_way.delay(order_id=order.id)
            return HttpResponseRedirect(reverse('lk-pre-orders'))
        return render(request, 'lk-pages/lk-create-order-page.html', {'form': form, 'formset': formset})

class LkOrdersPageView(ActiveUserConfirmMixin, EmailVerificationRequiredMixin, View):
    def get(self, request):
        username = request.user.profile.web_user.web_username
        data=get_orders_by_username_full(username)
        return render(request, 'lk-pages/lk-orders-page.html',context={'data':data})


class LkOrderPageView(ActiveUserConfirmMixin, EmailVerificationRequiredMixin, View):
    def get(self, request,order_id):
        user = request.user
        web_user = user.profile.web_user
        order = Orders.objects.filter(id=order_id, web_user=web_user).first()
        if order:
            data = OrderFullSerializer(order).data
            data_details = OrdersSerializerPre(order).data
            return render(request, 'lk-pages/lk-order-page.html',
                          context={'order': data,'data_details':data_details})
        messages.error(request, f'У вас нет доступа к данным этого заказа {order_id}.')
        return HttpResponseRedirect(reverse('lk-pre-orders'))


class LkPreordersPageView(ActiveUserConfirmMixin, EmailVerificationRequiredMixin, View):
    def get(self, request):
        username = request.user.profile.web_user.web_username
        data=get_orders_by_username_pre(username, pre=True)
        return render(request, 'lk-pages/lk-pre-orders-page.html',context={'data':data})



class LkPreordersDeletePageView(ActiveUserConfirmMixin, EmailVerificationRequiredMixin, View):
    def post(self,request):
        order_id=request.POST.get('order_id')
        user = request.user
        order = Orders.objects.filter(id=order_id,web_user=user.profile.web_user).first()
        if order:
            order.delete()
            messages.success(request, f'Заказ №{order_id} успешно удален.')
            return HttpResponseRedirect(reverse('lk-pre-orders'))
        messages.error(request, f'У вас нет доступа к данным этого заказа {order_id}.')
        return HttpResponseRedirect(reverse('auth_messages'))



class LkProfilePageView(View):
    def get(self, request):
        user = request.user
        if user.is_anonymous:
            return HttpResponseRedirect(reverse('login'))

        profile = get_object_or_404(Profile, user=user)
        form = ProfileModelForm(instance=profile)
        return render(request, 'lk-pages/lk-profile-page.html', {'form': form})

    def post(self, request):
        user = request.user
        if user.is_anonymous:
            return HttpResponseRedirect(reverse('login'))

        profile = get_object_or_404(Profile, user=user)
        form = ProfileModelForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('lk-profile')
        return render(request, 'lk-pages/lk-profile-page.html', {'form': form})

class LkMessagesPageView(ActiveUserConfirmMixin,
                         EmailVerificationRequiredMixin,
                         View):
    def get(self, request):
        user = request.user
        profile = get_object_or_404(Profile, user=user)
        web_user = profile.web_user
        if not web_user:
            messages.error(request, 'Произошла ошибка, этого не должно было случиться. Мы её уже решаем. Для срочной связи используйте телеграм. Либо форму для обратной связи.')
            messages.info(request, 'Наш телеграм бот: https://t.me/shipKZ')
            return HttpResponseRedirect(reverse('auth_messages'))
        token = create_access_token(user_id=web_user.user_id, username=web_user.web_username, secret=settings.SHARABLE_SECRET, delta_in_sec=20)
        return render(request,
                      template_name='lk-pages/lk-messages-page.html',
                      context={'token': token})

class LkLogoutPageView(View):
    def get(self, request):
        return HttpResponseRedirect(reverse('logout'))


def testing_view(request):
    return render(request, 'pages/test.html')


def make_text_for_status(data):
    """-заказ выкуплен в магазине
- заказ отправлен в казахстан (получен трек)  / заказ в пути
- заказ поступил на территорию казахстана
- заказ получен для последующей отправки
- заказ отправлен в рф
- закз получен клиентом"""

    order_status_info = data.get('order_status_info')
    is_forwarder = order_status_info.get('is_forwarder_way')
    check_list_1 = [
        'arrived_to_forwarder',
        'send_to_host_country',
        'received_in_host_country',
        'send_to_ru'

    ]

    check_list_2 = [
        'send_to_host_country',
        'arrived_to_host_country',
        'received_in_host_country',
        'send_to_ru'
    ]

    if is_forwarder:
        check_list = check_list_1
    else:
        check_list = check_list_2

    result = {}
    count = 2
    for check in check_list:
        data = order_status_info.get(check)
        if data:
            result[count] = True
        else:
            result[count] = False
        count += 1
    return result


class CallbackFormView(View):
    def get(self,request):
        form = CallbackResponseForm()
        return render(request, 'pages/callback.html', {'form': form})

    def post(self,request):
        form = CallbackResponseForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            email = data.get('email')
            connect = data.get('connect')
            name = data.get('name')
            message = data.get('message')
            callback_form=CallbackForm.objects.create(email=email,connect=connect,name=name,message=message)
            messages.success(request, f'Ваше обращение за номером {callback_form.id} успешно зарегистрировано. Мы обязательно отреагируем.')
            return HttpResponseRedirect(reverse('auth_messages'))
        return render(request, 'pages/callback.html', {'form': form})


def custom_404_view(request, exception):
    # Формируем сообщение для Telegram
    message = (
        f"🚨 <b>404 Error:</b>\n"
        f"<b>Path:</b> {request.path}\n"
        f"<b>Method:</b> {request.method}\n"
    )

    # Отправляем сообщение в Telegram
    try:
        sync_bot.send_message(
            chat_id=settings.ORDERS_CATCH_CHAT,
            text=message
        )
    except Exception as e:
        # Логируем ошибку, если отправка сообщения не удалась
        print(f"Failed to send 404 error message to Telegram: {e}")

    # Возвращаем стандартный JSON-ответ 404
    return JsonResponse({'error': 'Page not found'}, status=404)


class VinilPageView(View):
    def get(self, request):
        return render(request, 'pages/vinyl.html')

class ShopListView(View):
    def get(self, request):
        categories = ShopCategory.objects.all().order_by('priority')
        categories_list = [category.to_dict() for category in categories]
        return render(request, 'pages/shop_list.html',context={'categories':categories_list})

class YandexVerification(View):
    def get(self, request):
        return render(request, 'pages/yandex_50e907a0d24e53ea.html')