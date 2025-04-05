from django import forms
from django.forms import formset_factory
from captcha.fields import CaptchaField

class OrderForm(forms.Form):
    country = forms.ChoiceField(
        label='Где покупаем?',
        choices=[
            ('USA', 'США'),
            ('EUROPE', 'Европа'),
            ('ENGLAND', 'Англия'),
            ('OTHER', 'Другое'),
        ],
        widget=forms.RadioSelect,
        initial='EUROPE'
    )

class CalculatorTradeinnForm(forms.Form):
    exchange_rate = forms.ChoiceField(
        label="Валюта",
        choices=[
            ('EUR', 'Евро'),
            ('USD', 'Доллар'),
        ],
    )
    order_price = forms.CharField(
        label='Стоимость товара:',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Например: 100 Евро',
                                      'class': 'price-placeholder'})
    )
    delivery_price = forms.CharField(
        label='Стоимость доставки:',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Например: 10 Евро',
                                        'class': 'delivery-price-placeholder'})
    )




class UnregisteredOrderForm(OrderForm):
    url = forms.CharField(
        label='*Ссылка на товар:',
        max_length=800,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Например: https://www.amazon.com/',
                                      'class': 'custom-placeholder'})
    )
    price = forms.CharField(
        label='*Стоимость товара:',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Например: 100 Долларов',
                                      'class': 'custom-placeholder'})
    )
    count = forms.IntegerField(
        label='*Количество товара:',
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': 'Например: 5 штук',
                                        'class': 'custom-placeholder'})
    )
    comment = forms.CharField(
        label='Комментарий к заказу:',
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Любая информация которая вам покажется важной. Например: размер или цвет',
                                     'rows': 3,'cols': 25,
                                     'class': 'custom-placeholder'})
    )
    email = forms.EmailField(
        label='*Email:',
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Введите ваш email',
                                       'class': 'custom-placeholder'})
    )
    phone = forms.CharField(
        label='Телефон:',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Введите ваш телефон',
                                      'class': 'custom-placeholder'})
    )
    captcha = CaptchaField(label='*Введите текст с картинки:', required=True,
                           error_messages={'invalid': 'Капча решена неверно! Попробуйте еще раз.'})

class RegisterOrderItemForm(forms.Form):
    goods_link = forms.CharField(
        label='*Ссылка на товар:',
        max_length=800,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Например: https://www.amazon.com/',
                                      'class': 'custom-placeholder'})
    )
    count = forms.IntegerField(
        label='*Количество товара:',
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': 'Например: 5 штук',
                                        'class': 'custom-placeholder'})
    )
    comment = forms.CharField(
        label='Комментарий к товару:',
        required=False,
        widget=forms.TextInput(attrs={'placeholder':  'Например: размер или цвет',
                                     'rows': 1,
                                     'class': 'custom-placeholder'})
    )

RegisterOrderItemFormSet = formset_factory(RegisterOrderItemForm, extra=1, max_num=10)


