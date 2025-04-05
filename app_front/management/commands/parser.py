import json
from datetime import datetime

from django.core.management import BaseCommand
from legacy.models import Orders, OrderStatusInfo, Buyers
from panel.models import OrdersGroup


def create_buyers():
    buyers = {'абзал': 398139280,
              'ольга': 939886981,
              'абзал (теща)': 398139280,
              'askar': 1192158442,
              'fedor_test': 716336613,
              'ислам': 891106870,
              'насикат': 5636732686,
              'арман': 65519112,
              'алия': 656440057}

    for name, chat_id in buyers.items():
        buyer = Buyers.objects.get_or_create(telegram_id=chat_id, first_name=name)

class Command(BaseCommand):
    help = 'Parse orders from json file'

    def preparing_database(self):
        my_orders = Orders.objects.all()
        len_my_orders = len(my_orders)
        for num, order in enumerate(my_orders):
            order.group = None
            order.save()
            print(f'{num}/{len_my_orders} orders cleaned')
        OrdersGroup.objects.all().delete()



    def handle(self, *args, **kwargs):
        create_buyers()
        self.preparing_database()
        bad_orders = []
        no_order_status_info = []
        no_buyers = []
        row_dict = parser()

        for row, row_data in row_dict.items():
            print('---------------------------------')
            print('row:', row)
            print('row_data:', row_data)
            OrdersGroup.objects.filter(id=row).all().delete()

            datainfo = row_data['row_data']
            datainfo['buyer'] = Buyers.objects.filter(first_name=datainfo['buyer']).first()
            print('create ordergroupobject')
            order_group_obj=OrdersGroup.objects.create(id=row, **datainfo)

            for key, value in row_data['orders'].items():
                try:
                    order = Orders.objects.get(id=key)
                    order.group = order_group_obj
                    order.save()
                except Orders.DoesNotExist:
                    print('not found order with id:', key)
                    bad_orders.append(key)
                    continue

                try:
                    order_status_info = order.ori
                except AttributeError:
                    print('not found order_status_info with id:', key)
                    no_order_status_info.append(key)
                    order_status_info=OrderStatusInfo.objects.filter(order=order).first()
                    if not order_status_info:
                        order_status_info = OrderStatusInfo.objects.create(order=order,
                                                                                  relative_price='who knows',
                                                                                  shop='who knows',
                                                                                  store_order_number='who knows',
                                                                                  buyer_reward='who knows')

                try:
                    order_status_info.order_date = value['order_date']
                    order_status_info.shop = value['shop']
                    order_status_info.order_sum = value['order_sum']
                    order_status_info.order_currency = value['order_currency']
                    order_status_info.store_order_number = value['store_order_number']

                    if "теща" in value['buyer'].lower():
                        buyer_in_db = Buyers.objects.get(id=3)
                    else:
                        buyer_in_db = Buyers.objects.filter(first_name=value['buyer']).first()
                    if buyer_in_db:
                        order_status_info.buyer = buyer_in_db
                    else:
                        no_buyers.append((key, value['buyer']))
                        print('not found buyer:', value['buyer'])
                    order_status_info.forward_name = value['forward_name']
                    order_status_info.post_service = value['post_service']
                    order_status_info.trek = value.get('trek','без трека')
                    order_status_info.estimated_date_of_arrival = value['estimated_date_of_arrival']
                    order_status_info.payment_card = value.get('payment_card',None)
                    order_status_info.buyer_reward = value['buyer_reward']
                    order_status_info.comment = value.get('comment',None)
                    order_status_info.order_currency = value.get('order_currency',None)
                    order_status_info.order_sum = value.get('order_sum',None)
                    payed_delivery = value.get('is_delivery_payment')
                    order_status_info.cdek = value.get('cdek')
                    order_status_info.is_delivery_payment = payed_delivery
                    order_status_info.save()
                except Exception as ER:
                    print('Error in save data to statusInfo')
                    print(ER)
                    return False


def convert_date(date_str):
    try:
        if len(date_str.split('.')[-1]) == 2:
            date_obj = datetime.strptime(date_str, '%d.%m.%y')
        else:
            date_obj = datetime.strptime(date_str, '%d.%m.%Y')
        # Преобразуем дату в формат YYYY-MM-DD
        formatted_date = date_obj.strftime('%Y-%m-%d')
    except Exception as er:
        raise ValueError(f'ERROR IN convert_date function: {er}')
    return formatted_date


def parser():
    with open('/app/app_front/management/commands/orders.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        row_dict = {}
        for num,row in enumerate(data):
            if num == 0:
                continue
            orders = row[0].split('\n')
            if len(row) < 14:
                continue
            if len(row) < 17:
                while len(row) < 17:
                    row.append('')
            cdeks = row[14].split('\n')
            if len(orders) > len(cdeks):
                while len(orders) != len(cdeks):
                    cdeks.append('')
            orders_cdek = dict(zip(orders, cdeks))

            if 'теща' in row[7].lower():
                row[7] = 'абзал (теща)'
            payed_delivery = row[16]
            if payed_delivery:
                if "да" in payed_delivery.lower():
                    payed_delivery = True
                else:
                    payed_delivery = False
            else:
                payed_delivery = False

            row_info_data = {
                'order_date': convert_date(row[2]),
                'shop': row[3],
                'order_sum': row[4],
                'order_currency': row[5],
                'store_order_number': row[6],
                'buyer': row[7],
                'forward_name': row[8],
                'post_service': row[9],
                'trek': row[10],
                'estimated_date_of_arrival': row[11],
                'payment_card': row[12],
                'buyer_reward': row[13],
                'comment': row[15],
                'is_delivery_payment': payed_delivery
            }
            row_dict[num] = {'row_data': row_info_data, 'orders': {}}
            for order, cdek in orders_cdek.items():
                try:
                    int_order = int(order)
                    order_data = {
                        'id': int_order,
                        'row': num,
                        'cdek': cdek,
                    }
                    order_data = {**order_data, **row_info_data}
                    order_data['order_date'] = row[2]
                    if len(orders) > 1:
                        order_sum = row[4]
                        try:
                            order_sum.strip()
                            order_sum = int(order_sum)
                            order_sum = order_sum/len(orders)
                            order_data['order_sum'] = str(int(order_sum))
                        except:
                            order_data['order_sum'] = 'smth wrong'
                    else:
                        order_data['order_sum'] = row[4]
                    row_dict[num]['orders'][int_order] = order_data
                except:
                    continue
        return row_dict


