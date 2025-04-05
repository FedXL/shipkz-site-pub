from django.urls import path
from app_api.views import CalculatorApiView

urlpatterns = [
    path('calculator/',CalculatorApiView.as_view(),name='calculator'),
   ]

