import datetime

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import render
from django.urls import reverse

from django.views import View
from django.shortcuts import redirect
from rest_framework.response import Response

from app_auth.mixins import SuperuserRequiredMixin
from app_front.management.email.email_sender import my_logger
from legacy.models import Orders, Buyers, WebUsers, Users
from legacy.serializers import  OrderStatusInfoSerializer
from panel.forms import DateRangeForm, GroupInfoForm
from panel.models import OrdersGroup
from panel.notificator import Notificator
from panel.utils import columns_names, get_month_start_end_dates, get_month_grid, change_order_status_handler


class OrdersBaseView(SuperuserRequiredMixin, View):
    orders_filter = ...

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self, filter:list, order_by:str):
        return Orders.objects.filter(type__in=filter).order_by(order_by)

    def get(self):
        return Response({"message":"hello world"})


class OrdersTransitView(OrdersBaseView):
    orders_filter = ['KAZ_ORDER_LINKS','PAYMENT','WEB_ORDER']

    def get(self, request, ordered_by_filter='-id'):
        page_number = request.GET.get('page')
        columns_en, columns_rus = columns_names('transit')
        filtered_orders = Orders.objects.filter(type__in=self.orders_filter)
        rows = OrdersGroup.objects.prefetch_related(
            Prefetch('orders', queryset=filtered_orders)
        ).order_by(ordered_by_filter).distinct()
        paginator = Paginator(rows, 40)
        page_obj = paginator.get_page(page_number)
        context = {"columns": columns_rus, "page_obj": page_obj, 'rows': {}}

        for row in page_obj:
            row_info_data = row.to_dict()
            orders = row.orders.all()
            context["rows"][row.id] = {"group_name":row.group_name,'row_data':row_info_data,
                                       "orders":{},
                                       'ori':{},
                                       'row_link': f'/admin/panel/ordersgroup/{row.id}/change/'}
            orders_list = [order.ori for order in orders if hasattr(order, 'ori')]
            if len(orders_list) > 0:
                status_dict = OrderStatusInfoSerializer(orders_list, many=True).data
            else:
                status_dict = None

            context["rows"][row.id]["ori"] = status_dict
            for order in orders:
                result = order.to_dict()
                context["rows"][row.id]["orders"][order.id] = {"order_data":result}
        return render(request, 'admin-panel/orders-base.html', context=context)


    def post(self, request):
        selected_items = request.POST.get('selected_items', None)
        operation_type = request.POST.get('operation_type', None)
        my_logger.info(f"POST request data: {selected_items}")
        my_logger.info(f"POST type of operation: {operation_type}")
        row_list,order_list = [],[]

        if selected_items:
            selected_items_list = selected_items.split(',')
            for item in selected_items_list:
                if 'row' in item:
                    order_group = OrdersGroup.objects.get(id=item.replace('row_', ''))
                    row_list.append(order_group)
                if 'order' in item:
                    order = Orders.objects.get(id=item.replace('order_', ''))
                    order_list.append(order)

        match operation_type:
            case 'move':
                my_logger.info('start move object flow')
                if len(row_list) == 1:
                    print('switch orders')
                    for order in order_list:
                        order.group = order_group
                        order.save()
                    messages.success(request, f'Успешно перемещены заказы {order_list} в группу {order_group}')
                else:
                    messages.error(request, 'Я пока так не умею.')
                    messages.error(request, 'Выберите только одну группу.')
                my_logger.info(f"POST request data: {selected_items}")
                return redirect(reverse('orders-transit'))

            case 'status':
                my_logger.info('start change status flow')
                print('change status')
                status = request.POST.get('status_choice', None)
                if not status:
                    messages.error(request, 'Почему то статус не выбран (status_choice=None)')
                    return redirect(reverse('orders-transit'))
                if not row_list and not order_list:
                    messages.error(request, 'Надо выбрать галочками в какой строчке или в каких заказах менять статусы')
                    messages.error(request, f'Ваш выбор row_list={row_list} order_list={order_list}')
                    return redirect(reverse('orders-transit'))
                if len(row_list) > 1:
                    messages.error(request, 'Пока я статусы меняю только в одной строчке. А то запутаюсь еще.')
                    messages.error(request, 'Выберите только одну строчку-группу.')
                    return redirect(reverse('orders-transit'))
                orders_summary = []
                my_logger.info(f'CHANGE STATUS row list {row_list}')
                if row_list:
                    for row in row_list:
                        orders_list=row.orders.all()
                        my_logger.info(f'orders:{orders_list}')
                        orders_summary.extend(orders_list)
                my_logger.info(f'orders_summary:{orders_summary}')
                if order_list:
                    orders_summary.extend(order_list)
                my_logger.info(f'orders_summary:{orders_summary}')
                orders_summary = (set(orders_summary))
                my_logger.info(f'orders_summary:{orders_summary}')
                if not orders_summary:
                    messages.error(request, 'Фигня какая суммарно заказы пропали')
                    return redirect(reverse('orders-transit'))
                commands_to_send = {}
                for order in orders_summary:
                    result, comment = change_order_status_handler(status, order)
                    if result:
                        messages.success(request, f'Статус заказа {order.id} успешно изменен на {status}')
                        notificator=Notificator(order, status)
                        result=notificator.send_notification()
                        if result:
                            messages.info(request, f'Следующие уведомления были отправлены по заказу {order.id} - {result}')
                    else:
                        messages.error(request, f'Ошибка при изменении статуса заказа {order.id} на {status}'
                                                f' Error: {comment}')
                my_logger.info(f'commands_to_send:{commands_to_send}')
                return redirect(reverse('orders-transit'))


class OrdersTradeinnView(OrdersBaseView):
    orders_filter = ['TRADEINN']

    def get(self, request, ordered_by_filter='-id'):
        page_number = request.GET.get('page')
        columns_en, columns_rus = columns_names('tradeinn')
        filtered_orders = Orders.objects.filter(type__in=self.orders_filter).prefetch_related('ori_tradeinn').order_by(ordered_by_filter)
        paginator = Paginator(filtered_orders, 20)
        page_obj = paginator.get_page(page_number)
        rows = {}
        for order in page_obj:
            result = order.to_dict()
            rows[order.id] = result
        context = {"columns": columns_rus, "page_obj": page_obj,'rows':rows}
        return render(request, 'admin-panel/orders-tradeinn.html', context=context)

class BayersView(SuperuserRequiredMixin,View):
    """
    1) раскладка на каждый месяц по каждому баеру нагрузка по заказам
    2) деньги на каждого баера
    3) количество заказов на каждого баера
    """

    def get_context(self,start_date,end_date):
        buyers_dict={}
        buyers = Buyers.objects.all()
        for buyer in buyers:
            filtered_orders = Orders.objects.filter(
                type__in=['KAZ_ORDER_LINKS', 'PAYMENT', 'WEB_ORDER'],
                ori__isnull=False,
                ori__buyer=buyer,
                ori__paid__range=(start_date, end_date),
            ).select_related('ori')
            orders_list = []
            order_money = []
            for order in filtered_orders:
                orders_list.append(order.id)
                order_money.append((order.ori.order_sum, order.ori.order_currency))
            if len(filtered_orders) > 0:
                buyers_dict[buyer.first_name] = {'orders': len(filtered_orders), 'money': order_money,
                                                 'order': orders_list}
        context = {'buyers_data': buyers_dict}
        return context


    def get(self, request):
        buyers_dict = {}
        start_date=request.COOKIES.get('start_date',None)
        end_date=request.COOKIES.get('end_date',None)
        if not start_date or not end_date:
            year = datetime.datetime.now().year
            month = datetime.datetime.now().month
            start_date, end_date=get_month_start_end_dates(year=year, month=month)
        context=self.get_context(start_date, end_date)
        context['form'] = DateRangeForm(initial={'start_date': start_date, 'end_date': end_date})
        return render(request, 'admin-panel/buyers.html', context=context)

    def post(self,request):
        form = DateRangeForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            context = self.get_context(start_date, end_date)
            context['form'] = DateRangeForm(initial={'start_date': start_date, 'end_date': end_date})
            response = render(request, 'admin-panel/buyers.html', context=context)
            response.set_cookie('start_date', start_date, max_age=60 * 60 * 24 * 30)  # Куки на 30 дней
            response.set_cookie('end_date', end_date, max_age=60 * 60 * 24 * 30)

            return response
        else:
            return Response({"message":"Form is not valid"})


class OrdersStatisticView(SuperuserRequiredMixin,View):
    grid = get_month_grid(2023,1)

    def get(self, request):
        tradeinn_queryset = Orders.objects.filter(type__in=['TRADEINN'])
        transit_web_all_queryset = Orders.objects.filter(type__in=['WEB_ORDER'])
        transit_web_confirm_queryset = Orders.objects.filter(type__in=['WEB_ORDER'],ori__paid__isnull=False)
        transit_telegram_all_queryset = Orders.objects.filter(type__in=['PAID','KAZ_ORDER_LINKS'])
        transit_telegram_confirm_queryset = Orders.objects.filter(type__in=['PAID','KAZ_ORDER_LINKS'],ori__paid__isnull=False)
        result = {}
        tradeinn_graph = []
        transit_web_all_graph = []
        transit_web_confirm_graph = []
        transit_telegram_all_graph = []
        transit_telegram_confirm_graph = []
        for month, month_data in self.grid.items():

            tradeinn_count = tradeinn_queryset.filter(time__range=(month_data['start_date'],
                                                                   month_data['end_date'])).count()
            transit_web_all_count = transit_web_all_queryset.filter(time__range=(month_data['start_date'],
                                                                                      month_data['end_date'])).count()
            transit_web_confirm_count = transit_web_confirm_queryset.filter(ori__paid__range=(month_data['start_date'],
                                                                                              month_data['end_date'])).count()
            transit_telegram_all_count = transit_telegram_all_queryset.filter(time__range=(month_data['start_date'],
                                                                                          month_data['end_date'])).count()
            transit_telegram_confirm_count = transit_telegram_confirm_queryset.filter(ori__paid__range=(month_data['start_date'],
                                                                                                        month_data[
                                                                                                            'end_date'])).count()
            tradeinn_graph.append({'x': month,'value': tradeinn_count})
            transit_web_confirm_graph.append({'x': month, 'value': transit_web_confirm_count})
            transit_web_all_graph.append({'x': month, 'value': transit_web_all_count})
            transit_telegram_all_graph.append({'x': month, 'value': transit_telegram_all_count})
            transit_telegram_confirm_graph.append({'x': month, 'value': transit_telegram_confirm_count})

        result['tradeinn_graph'] = tradeinn_graph
        result['transit_web_all_graph'] = transit_web_all_graph
        result['transit_web_confirm_graph'] = transit_web_confirm_graph
        result['transit_telegram_all_graph'] = transit_telegram_all_graph
        result['transit_telegram_confirm_graph'] = transit_telegram_confirm_graph

        return render(request, 'admin-panel/orders-statistic.html', context=result)

class EditOrderInfoView(SuperuserRequiredMixin,View):
    def get(self, request):
        row_id = request.GET.get('row_id',None)
        form = GroupInfoForm()
        return render(request, template_name='admin-panel/edit-group-info.html',context={'form':form,'row_id':row_id})

    def post(self, request):
        return Response({"message":"hello world"})



class ProfileView(SuperuserRequiredMixin,View):
    def get(self, request):
        client_type=request.GET.get('client_type', None)
        client_id=request.GET.get('client_id', None)
        if not client_type or not client_id:
            return Response({"message":"client_type or client_id is not provided"})
        result = {'meta':{}}
        if 'web' in client_type:
            tele_user_id = None
            web_user = WebUsers.objects.get(user_id=client_id)
            web_user_meta = web_user.user_meta.all()
            if web_user_meta:
                for meta in web_user_meta:
                    result['meta'][meta.meta_id] = meta.to_dict()
            tele_web_user_id = client_id
            result['bot_web_user'] = web_user.to_dict()
            profile_obj = web_user.profile.first()
            my_logger.info(f"profile : {profile_obj}")
            if profile_obj:
                profile_id = profile_obj.id
                profile_dict = profile_obj.to_dict()
                result['website_profile'] = profile_dict
                if profile_obj.telegram_user:
                    telegram_dict = profile_obj.telegram_user.to_dict()
                    result['bot_telegram_user'] = telegram_dict
                    tele_user_id = profile_obj.telegram_user.user_id
                user_django = profile_obj.user
                my_logger.warning(f"user_django: {user_django}")
                site_user_id=user_django.id
                if user_django:
                    user_django_dict = user_django.to_dict()
                else:
                    user_django_dict = 'без пользователя и это странно при том что профиль есть'
                result['website_user'] = user_django_dict
            else:
                site_user_id = None
                profile_id = None

        elif 'telegram' in client_type:
            tele_web_user_id = None
            tele_user_id = client_id
            telegram_user = Users.objects.get(user_id=client_id)
            result['bot_telegram_user'] = telegram_user.to_dict()
            profile_obj = telegram_user.profile.first()
            if profile_obj:
                profile_id = profile_obj.id
                result['website_profile'] = profile_obj.to_dict()
                if profile_obj.web_user:
                    result['bot_web_user'] = profile_obj.web_user.to_dict()
                    tele_web_user_id = profile_obj.web_user.user_id
                user_django = profile_obj.user
                user_django_dict = user_django.to_dict()
                site_user_id = user_django.id
                result['website_user'] = user_django_dict
            else:
                profile_id = None
                site_user_id = None
        else:
            return Response({"message":"client_type is not valid"})

        links = {'web_user_link': f'{settings.BASE_URL}/admin/legacy/webusers/{tele_web_user_id}/change/' if tele_web_user_id else None,
                 'telegram_user_link': f'{settings.BASE_URL}/admin/legacy/users/{tele_user_id}/change/' if tele_user_id else None,
                 'profile_link': f'{settings.BASE_URL}/admin/app_auth/profile/{profile_id}/change/' if profile_id else None,
                 'user_site_link': f'{settings.BASE_URL}/admin/app_auth/customuser/{site_user_id}/change/' if site_user_id else None,
                 }
        context = {'profile': result, 'title': f"Профиль {client_type} {client_id}", 'links': links}
        return render(request, 'admin-panel/profile-view.html', context=context)





















































