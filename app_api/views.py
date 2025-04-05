from django.http import HttpResponseForbidden, JsonResponse
from rest_framework.views import APIView
from app_api.calculator.core import Calculator


class CalculatorApiView(APIView):
    def post(self, request):
        data = request.data
        order_price = data.get('order_price')
        delivery_price = data.get('delivery_price')
        currency = data.get('currency')
        calculator=Calculator(order_price=order_price,
                              delivery_price=delivery_price,
                              currency=currency)
        result = calculator.to_dict
        return JsonResponse(result)