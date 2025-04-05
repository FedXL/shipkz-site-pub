from datetime import datetime, timedelta
import calendar
from pydantic import BaseModel
from pydantic_core import ValidationError
from app_front.management.email.email_sender import my_logger
from legacy.models import Orders, OrderStatusInfo


def columns_names(columns_type:str):
    match columns_type:
        case 'transit':
            col = {'row': 'Ряд',
                'order_id': 'Номер заказа',
                'statuses': 'Статусы',
                'client': 'Клиент',
                'order_date': 'Дата заказа',
                'shop': 'Магазин',
                'order_sum': 'Сумма заказа',
                'currency': 'Валюта',
                'store_order_number': 'Номер заказа в магазине/номер заказа у Форвардера',
                'buyer': 'Байер',
                'forward_name': 'Форвардер',
                'post_service': 'Почтовая служба',
                'trek': 'Трек',
                'estimated_date_of_arrival': 'Ориентировочная дата в КЗ',
                'payment_card': 'Карта оплаты',
                'reward': 'Вознаграждение',
                'cdek': 'CDEK',
                'comment': 'Комментарий',
                'delivery_payment': 'Оплата доставки'}
        case 'tradeinn':

            col = {'order_id': 'Номер заказа',
                   'client': 'Клиент',
                   'order_date': 'Дата заказа',
                   'status': 'Статус',
                   'order_price': 'Сумма заказа',
                   'manager': 'Менеджер'}
    return col.keys(), col.values()


def get_month_start_end_dates(year, month):
    start_date = datetime(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, last_day)
    return start_date, end_date


def get_month_info(month, year):
    first_day = datetime(year, month, 1)
    last_day = (datetime(year, month + 1, 1) - timedelta(days=1)) if month < 12 else datetime(year + 1, 1, 1) - timedelta(days=1)
    month_name = calendar.month_name[month]
    return {
        "month_number": month,
        "start_date": first_day.strftime('%Y-%m-%d'),
        "end_date": last_day.strftime('%Y-%m-%d'),
        "month_name": month_name,
        "transit":None,
        "tradeinn":None,
    }

def get_month_grid(start_year, start_month):
    current_date = datetime.now()
    months_dict = {}
    current_month = start_month
    current_year = start_year

    while datetime(current_year, current_month, 1) <= current_date:
        month_key = f"{current_month:02d}.{current_year}"
        months_dict[month_key] = get_month_info(current_month, current_year)
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1
    return months_dict


class Paid(BaseModel):
    shop: str
    store_order_number: str | int
    relative_price: str
    is_forward: bool
    host_country: str = None

class ArrivedWarehouse(BaseModel):
    pass


class SendToHostCountry(BaseModel):
    trek: str | int = None
    post_service: str
    buyer: int | str = None
    buyer_reward: str = None


class SendToRU(BaseModel):
    cdek: dict


def change_order_status_handler(status: str, order: Orders):
    my_logger.info('[INFO][START] Change order status handler with:', status, order.id)
    try:
        group = order.group
        data = group.to_dict()
        host_country = group.buyer.country
        if not host_country:
            return False, f"Не указана страна прибытия. Для этого надо выбрать баера, а у баера должна быть указана страна"
        data['host_country'] = host_country
        my_logger.info(f"[INFO] Data: {data}")

        host_country = data.get('host_country', None)

        if not host_country:
            comment = f"Нужно указать Buyer в строчке № {group.id}"
            return False, comment
        shop = data.get('shop')
        if not shop:
            comment = f"Нужно указать название магазина в группе заказов № {group.id}"
            return False, comment
        store_order_number = data.get('store_order_number')
        if not store_order_number:
            comment = f"Нужно указать номер заказа в магазине в группе заказов № {group.id}"
            return False, comment
        order_group_money = data.get('order_sum')
        if not order_group_money:
            comment = f"Нужно указать суммарную сумму заказа в группе заказов № {group.id}"
            return False, comment
        data_for_db = {
                       'host_country': host_country,
                       'shop': shop,
                       'store_order_number': store_order_number,
                       'relative_price': order_group_money,
                       'is_forward': data.get('is_forward')
        }
        host_country=data.get('host_country')
        match status:
            case "paid":
                """страна меняется только один раз здесь"""
                timedata = {'paid': datetime.now()}
                data_for_db = {**timedata, **data_for_db}
                order.status = 'PAID'
                order.save()

            case "arrived_to_forward":
                timedata = {'arrived_to_forward': datetime.now()}
                is_forwarder = data.get('is_forward')
                if not is_forwarder:
                    comment = (f"Нужно поставить галочку - заказ идет через форвардера в группе № {group.id}."
                               f" А то статус меняется на arrived_to_forward, в то время как система уверена,"
                               f" что заказ идет напрямую")
                    return False, comment
                data_for_db = {**timedata, **data_for_db}
                order.status = 'ARRIVED_IN_HOST_COUNTRY'
                order.save()

            case "got_track":
                """Отправлено в страну назначения"""
                timedata = {'got_track': datetime.now()}


                trek = data.get('trek')
                if not trek:
                    comment = f"Для Статуса отправлено в страну назначения, нужно указать трек в группе № {group.id}"
                    return False, comment
                post_service = data.get('post_service')
                if not post_service:
                    comment = f"Для Статуса отправлено в страну назначения, нужно указать почтовую службу в группе № {group.id}"
                    return False, comment
                buyer = data.get('buyer')
                if not buyer:
                    comment = (f"Для Статуса отправлено в страну назначения, нужно указать баера в группе № {group.id}."
                               f" А то как я ему сообщение отправлю что посылка едет?")
                    return False, comment
                buyer_reward = data.get('buyer_reward')
                if not buyer_reward:
                    comment = (f"Для Статуса отправлено в страну назначения, нужно указать вознаграждение баера в группе № {group.id}."
                               f" А то как я ему в сообщении передам сумму вознаграждения за посылку??")
                    return False, comment
                data_for_db = {**timedata, **data}
                order.status = "SENT_TO_HOST_COUNTRY"

            case "arrived_to_host_country":
                timedata = {'arrived_to_host_country': datetime.now()}
                data_for_db = timedata
                is_forwarder = data.get('is_forward')
                if is_forwarder:
                    comment = f"Нужно убрать галочку что заказ идет через форвардера в группе № {group.id}. А то статус меняется на arrived_to_host_country (этот статус доступен только для посылок напрямую) а система думает что заказ идет через форвардера"
                    return False, comment
                trek=data.get('trek')
                if not trek:
                    comment = f"Для Статуса прибыло в страну назначения, нужно указать трек в группе № {group.id}"
                    return False, comment
                post_service = data.get('post_service')
                if not post_service:
                    comment = f"Для Статуса прибыло в страну назначения, нужно указать почтовую службу в группе № {group.id}"
                    return False, comment
                buyer = data.get('buyer')
                if not buyer:
                    comment = f"Для Статуса прибыло в страну назначения, нужно указать баера в группе № {group.id}."
                    return False, comment
                buyer_reward = data.get('buyer_reward')
                if not buyer_reward:
                    comment = f"Для Статуса прибыло в страну назначения, нужно указать вознаграждение баера в группе № {group.id}."
                    return False, comment
                data_for_db = {**timedata, **data}
                order.status = "ARRIVED_IN_HOST_COUNTRY"
                order.save()

            case "received_in_host_country":
                timedata = {'received_in_host_country': datetime.now()}
                trek=data.get('trek')
                if not trek:
                    comment = f"Для Статуса получено в стране назначения, нужно указать трек в группе № {group.id}"
                    return False, comment
                post_service = data.get('post_service')
                if not post_service:
                    comment = f"Для Статуса получено в стране назначения, нужно указать почтовую службу в группе № {group.id}"
                    return False, comment
                buyer = data.get('buyer')
                if not buyer:
                    comment = f"Для Статуса получено назначения, нужно указать баера в группе № {group.id}."
                    return False, comment
                buyer_reward = data.get('buyer_reward')
                if not buyer_reward:
                    comment = f"Для Статуса прибыло в страну назначения, нужно указать вознаграждение баера в группе № {group.id}."
                    return False, comment
                data_for_db = {**timedata, **data}
                order.status = "RECEIVED_IN_HOST_COUNTRY"
                order.save()

            case "send_to_ru":
                timedata = {'send_to_ru': datetime.now()}
                try:
                    CDEK = order.ori.cdek
                except Exception as e:
                    comment = """Информация о заказах не найдена (ORI Order Status Info - отсутсвует)"
                                    " Скорее всего вы первый раз статус обновляете у заказа. "
                                    "Предыдущие статусы создадут ORI для этого заказа """
                    return False , comment
                if not CDEK:
                    comment = (f"Для Статуса отправлено в РФ, нужно указать данные CDEK в СТАТУСАХ Заказа {order.id}!"
                               f" Это надо ткнуть на соответсвующий квадратик в статусах и там заполнить сдек номер сдека")
                    return False, comment
                data_for_db = {**timedata, **data}
                order.status = "SENT_TO_RUSSIA"
                order.save()

            case "success":
                timedata = {'success': datetime.now()}
                data_for_db = {**timedata, **data}
                order.status="GET_BY_CLIENT"
            case _:
                raise ValueError(f"Invalid status: {status}")
        data_for_db['host_country'] = data.get('host_country')
        try:
            order_status_info = order.ori
        except:
            my_logger.warning(f"[INFO] OrderStatusInfo is None")
            order_status_info=OrderStatusInfo.objects.create(order=order, **data_for_db)
        for key,value in data_for_db.items():
            setattr(order_status_info,key,value)
        order_status_info.save()
        return True, group.id
    except ValidationError as e:
        return False, f"Invalid data. ValidationError : {e}"
    except ValueError as e:
        return False, f"Invalid order_id: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"




