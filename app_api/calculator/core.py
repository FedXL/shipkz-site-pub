from legacy.models import Exchange

class Calculator:
    def __init__(self, order_price, delivery_price, currency):

        sber_usd = Exchange.objects.filter(valuta='raif_usd').first()
        sber_euro = Exchange.objects.filter(valuta='raif_euro').first()

        usd = Exchange.objects.filter(valuta='usd').first()
        euro = Exchange.objects.filter(valuta='eur').first()
        assert currency in ['usd', 'euro','USD','EUR'], f"Currency must be 'usd' or 'euro': {currency}"

        if currency == 'USD':
            currency = 'usd'
        if currency in  ['EUR','EURO']:
            currency = 'euro'


        self.currency = currency
        if sber_usd is None:
            raise ValueError("Exchange rate for Sber USD is not found")
        if sber_euro is None:
            raise ValueError("Exchange rate for Sber EURO is not found")
        if usd is None:
            raise ValueError("Exchange rate for USD is not found")
        if euro is None:
            raise ValueError("Exchange rate for EURO is not found")

        self.sber_usd = sber_usd.price
        self.sber_euro = sber_euro.price
        self.sber_usd_date = sber_usd.data
        self.sber_euro_date = sber_euro.data

        self.usd = usd.price
        self.euro = euro.price
        order_price = order_price.replace(',', '.')
        delivery_price = delivery_price.replace(',', '.')
        self.order_price = float(order_price)
        self.delivery_price = float(delivery_price)

        self.__get_currency()
        self.__calculate_taxes()
        self.__buy_out_price()
        self.__CDEK()
        self.__total_summary()

    def __get_currency(self):

        if self.currency == 'usd':
            self.central_bank = self.usd
            self.sberbank = self.sber_usd
            self.prefix = '$'
            self.date_text = self.sber_euro_date
        else:
            self.central_bank = self.euro
            self.sberbank = self.sber_euro
            self.prefix = '€'
            self.date_text = self.sber_euro_date
        self.koeff_usd_eur = round(float(self.usd) / float(self.euro), 15)

    def __calculate_commission_coefficient(self, total_price):
        if self.currency == 'usd':
            if total_price <= 500:
                self.commission_coefficient = 1.3
            else:
                self.commission_coefficient = 1.25
        elif self.currency == 'euro':
            if total_price <= 500 * self.koeff_usd_eur:
                self.commission_coefficient = 1.3
            else:
                self.commission_coefficient = 1.25

    def __calculate_taxes(self):
        if self.currency == 'usd':
            in_euro = self.order_price * self.koeff_usd_eur
            taxes_body_in_euro = in_euro - 200
            if taxes_body_in_euro <= 0:
                self.taxes = 0
                self.taxes_for_client = 0
                self.taxes_body = 0
                self.taxes_commision = 0
            else:
                self.taxes = round((taxes_body_in_euro * 0.15 * self.usd)/self.koeff_usd_eur, 2)
                self.taxes_for_client = round((taxes_body_in_euro * 0.15 * self.sber_usd)/self.koeff_usd_eur)
                self.taxes_body = round(taxes_body_in_euro / self.koeff_usd_eur)
                self.taxes_commision = self.taxes * 0.05
        else:
            taxes_body_in_euro = self.order_price - 200
            if taxes_body_in_euro <= 0:
                self.taxes = 0
                self.taxes_for_client = 0
                self.taxes_body = 0
                self.taxes_commision = 0
            else:
                self.taxes_body = round(taxes_body_in_euro)
                self.taxes = round(taxes_body_in_euro * 0.15 * self.euro, 2)
                self.taxes_for_client = round(taxes_body_in_euro * 0.15 * self.sber_euro, 2)
                self.taxes_commision = self.taxes * 0.05

    def __CDEK(self):
        order_price = self.order_price
        self.CDEK_075 = round(order_price * 0.0075 * self.sberbank)
        self.CDEK = round(order_price * 0.0075 * self.central_bank + 1500, 3)
        self.CDEK_for_clients = round(order_price * 0.0075 * self.sberbank + 1500)

    def __buy_out_price(self):
        self.order_price_for_client = round(self.order_price * self.sberbank)
        self.order_price_for_company = self.order_price * self.central_bank
        self.delivery_price_for_client =round( self.delivery_price * self.sberbank)
        self.delivery_price_for_company = self.delivery_price * self.central_bank
        summary_price = self.order_price + self.delivery_price
        self.buy_out_price = summary_price * self.central_bank
        self.buy_out_price_for_clients = summary_price * self.sberbank

        self.__calculate_commission_coefficient(summary_price)
        self.buy_out_with_commision = round(self.buy_out_price * self.commission_coefficient)
        self.company_commission = round(self.buy_out_price * (self.commission_coefficient - 1)) + self.taxes_commision
        self.client_commision = round(self.buy_out_with_commision - self.buy_out_price_for_clients)



    def __total_summary(self):
        self.total = round(self.buy_out_price_for_clients
                           + self.taxes_for_client
                           + self.CDEK_for_clients
                           + (1000 if self.taxes else 0)
                           + self.client_commision)


    def __create_strings(self):
        result = []
        result.append(
            {
                'text': 'Курс Райффайзен банка для безналичных расчетов',
                'description': self.date_text,
                'value': f"{self.sberbank} ₽",
                'link': 'https://www.raiffeisen.ru/currency_rates/',
            }
        )

        result.append(
            {
            "text": "Cтоимость заказа",
            "description": f"{self.order_price} Х {self.sberbank} {self.prefix}",
            "value": f"{self.order_price_for_client} ₽",
            }
        )
        result.append(
            {
                'text': "Стоимость Доставки",
                "description": f"{self.delivery_price} Х {self.sberbank} {self.prefix}",
                "value": f"{self.delivery_price_for_client} ₽"
            }
        )

        if self.taxes:
            result.append(
                {
                    "text": 'Таможенный сбор выше 200 евро',
                    "description": f"Сумма облагаемая сбором в 15% {self.taxes_body} {self.prefix}",
                    "value": f"{self.taxes_for_client} ₽"
                }
            )
            result.append(
                {
                    "text": "Услуги таможенного брокера",
                    "description": "Примерная сумма",
                    "value": f"1000 ₽"
                }
            )
        result.append(
            {
                "text": "Доставка СДЕК из Казахстана в Россию",
                "description": f"Среднее значение 1500 Р + Страхование 0.75% Х {self.order_price_for_client} ₽",
                "value": f"{self.CDEK_for_clients} ₽"
            }
        )

        if not self.taxes_commision :
            commision_text = 'нет сбора'
        else:
            commision_text = f"в том числе 5% за таможенный сбор {self.taxes_commision} ₽"

        result.append(
            {
                "text": "Наша комиссия",
                "description": "Расходы на перевод денег, конвертацию, таможенное сопровождение и пересылку.",
                "value": f"{self.client_commision} ₽"
            }
        )
        result.append(
            {
                "text": "Итого",
                "descriprion":"Сумма",
                "value": f"{self.total} ₽",
            }
        )
        return result

    def __create_strings_reserved(self):
        """проверялка для тестов"""
        result = []
        result.append(
            {
                'text': 'Курс Райффайзен банка для безналичных расчетов',
                'description': self.date_text,
                'value': f"{self.sberbank} ₽ | {self.central_bank}",
                'link': 'https://www.raiffeisen.ru/currency_rates/',
            }
        )

        result.append(
            {
            "text": "Cтоимость заказа",
            "description": f"{self.order_price} Х {self.sberbank} {self.prefix}",
            "value": f"{self.order_price_for_client} ₽ | {self.order_price_for_company}",
            }
        )
        result.append(
            {
                'text': "Стоимость Доставки",
                "description": f"{self.delivery_price} Х {self.sberbank} {self.prefix}",
                "value": f"{self.delivery_price_for_client} ₽ | {self.delivery_price_for_company}"
            }
        )

        if self.taxes:
            result.append(
                {
                    "text": 'Таможенный сбор выше 200 евро',
                    "description": f"Сумма облагаемая сбором в 15% {self.taxes_body} {self.prefix}",
                    "value": f"{self.taxes_for_client} ₽ | {self.taxes} коэффициент usd/euro {self.koeff_usd_eur}"
                }
            )
            result.append(
                {
                    "text": "Услуги таможенного брокера",
                    "description": "Примерная сумма",
                    "value": f"1000 ₽"
                }
            )
        result.append(
            {
                "text": "Доставка СДЕК из Казахстана в Россию",
                "description": f"Среднее значение 1500 Р + Страхование 0.75% Х {self.order_price_for_client} ₽",
                "value": f"{self.CDEK_for_clients} ₽ | {self.CDEK} "
            }
        )

        if not self.taxes_commision :
            commision_text = 'нет сбора'
        else:
            commision_text = f"в том числе 5% за таможенный сбор {self.taxes_commision} ₽"

        result.append(
            {
                "text": "Наша комиссия",
                "description": "Расходы на перевод денег, конвертацию, таможенное сопровождение и пересылку.",
                "value": f"{self.client_commision} ₽  | {self.company_commission} | {commision_text}"
            }
        )
        result.append(
            {
                "text": "Итого",
                "descriprion":"Сумма",
                "value": f"{self.total} ₽",
            }
        )
        return result

    @property
    def to_dict(self):
        result = {
            'buy_out':self.buy_out_price,
            'buy_out_cli': self.buy_out_price_for_clients,
            'euro_for_client': self.euro,
            'euro_for_company': self.sber_euro,
            'company_commission': self.company_commission,
            'client_commision': self.client_commision,
            'taxes': self.taxes,
            'taxes_for_client': self.taxes_for_client,
            'CDEK': self.CDEK,
            'CDEK_for_clients': self.CDEK_for_clients,
            'total': self.total,
            'currency': self.currency,
            'rows': self.__create_strings()
        }
        return result












