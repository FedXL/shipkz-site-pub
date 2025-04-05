import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
import logging

from app_front.management.utils import generate_current_date

my_logger = logging.getLogger('email_sender')
my_logger.setLevel(logging.DEBUG)
my_logger.addHandler(logging.StreamHandler())
my_logger.addHandler(logging.FileHandler('email_sender.log'))

def send_order_notification_email(to_mail,
                                  order_number,
                                  form_data,
                                  username=None,
                                  is_self_mail=False):
    """

    :param is_self_mail:
    :param to_mail:
    :param order_number:
    :param form_data: country, url, price, comment, phone
    :param username:
    :return:
    """
    my_logger.debug('Start send_order_notification_email')

    country = form_data.get('country')
    url = form_data.get('url')
    price = form_data.get('price')
    comment = form_data.get('comment')
    phone = form_data.get('phone')
    data = generate_current_date()
    header = f"Заказ №{order_number} SHIPKZ.RU от {data} года"
    if not username:
        username = 'Незарегистрированный Пользователь!'
    try:
        if is_self_mail:
            email_body = (
                          f'<h2>Прилетел заказ </h2>'
                          f'<p>Пользователь: {username} </p>'
                          f'<p>Номер заказа: {order_number} </p>'
                          f'<p>Почта: {is_self_mail} </p>'
                          f'<p>Данные заказа: </p>'
                          f'<p>Откуда {country}</p>'
                          f'<p>Ссылка на товар: {url}</p>'
                          f'<p>Цена товара: {price}</p>'
                          f'<p>Комментарий к заказу: {comment}</p>'
                          f'<p>Телефон: {phone}</p>'
                          )
        else:
            email_body = (f'<h2>Уважаемый {username}</h2>'
                          f'<p>Ваш заказ №{order_number} принят в обработку!</p>'
                          f'<p>Данные заказа: </p>'
                          f'<p>Откуда {country}</p>'
                          f'<p>Ссылка на товар: {url}</p>'
                            f'<p>Цена товара: {price}</p>'
                            f'<p>Комментарий к заказу: {comment}</p>'
                            f'<p>Ваш телефон: {phone}</p>'
                          f'<p>Ожидайте, с вами обязательно свяжется менеджер.</p>')

        send_email(header=header, body=email_body, to_mail=to_mail)
    except Exception as e:
        my_logger.error(f'Error in send_order_notification_email: {e}')
        return False

def send_register_order_notification_email(to_mail,
                                           username,
                                           order_number,
                                           country,
                                           goods,
                                           is_self_mail=False):
    data = generate_current_date()
    my_logger.debug('Start send_register_order_notification_email')
    header = f"Заказ №{order_number} SHIPKZ.RU от {data} года"
    if not is_self_mail:
        email_body = (f'<h2>Уважаемый {username}</h2>'
                        f'<p>Ваш заказ №{order_number} принят в обработку!</p>'
                        f'<p>Откуда {country}</p>'
                        f'<p>Товары:</p>')
    else:
        email_body = (f'<h2>Прилетел заказ </h2>'
                        f'<p>Пользователь: {username} </p>'
                        f'<p>Почта: {is_self_mail} </p>'
                        f'<p>Номер заказа: {order_number} </p>'
                        f'<p>Откуда {country}</p>'
                        f'<p>Товары:</p>')

    for number,item in goods.items():
        url = item.get('url')
        count = item.get('amount')
        comment = item.get('comment')
        email_body += (f'<p>Ссылка на товар: <a href="{url}"> {number}-ссылка</p>'
                        f'<p>Количество товара: {count}</p>'
                        f'<p>Комментарий к товару: {comment}</p>'
                        f'<p>------------------------------------</p>')
    email_body += "<br><br><br>"
    if not is_self_mail:
        email_body += (f'<p>Ожидайте, с вами обязательно свяжется менеджер.</p>')
    send_email_result=send_email(header=header, body=email_body, to_mail=to_mail)
    return send_email_result


def send_email(header, body, to_mail):

    my_logger.debug('Start send_email')
    my_logger.debug(f'header: {header}')
    my_logger.debug(f'body: {body}')
    my_logger.debug(f'to_mail: {to_mail}')

    try:
        from_mail = "shipkz.ru@gmail.com"
        # from_mail = "fedorkuruts@gmail.com"
        from_passwd = "rfmd tols ggcv vbqo"
        # from_passwd = "ppuc icbr vbxs pckz"
        server_adr = "smtp.gmail.com"
        port = 587
        msg = MIMEMultipart()
        msg["From"] = from_mail
        msg['To'] = to_mail
        msg["Subject"] = Header(header, 'utf-8')
        msg["Date"] = formatdate(localtime=True)
        msg.attach(MIMEText(body, 'html', 'utf-8'))

        my_logger.debug('Создали сообщение')
        smtp = smtplib.SMTP(server_adr, port=port)
        my_logger.debug('создали объект для отправки сообщения')
        smtp.starttls()
        my_logger.debug('Открвываем сединение')
        smtp.ehlo()
        smtp.login(from_mail, from_passwd)
        my_logger.debug('Залогинился в свой ящик')
        smtp.sendmail(from_mail, to_mail, msg.as_string())
        server_response = smtp.noop()
        my_logger.info(f'Ответ сервера {server_response}')
        print(f'Ответ сервера {server_response}')
        smtp.quit()
        my_logger.info('Email was sent successfully!!')
        return True
    except Exception as e:
        my_logger.error(f'Error in send_email: {e}')
        return False


