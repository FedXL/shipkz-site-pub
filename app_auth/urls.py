from django.urls import path
from app_auth.views import SignUpView, LoginView, LogoutCustomView, AllertsView, ConfirmEmailMessageView, \
    UniqueUserNameApiView, UnregRegistrationApiView, ConfirmEmailPointView, warning_messages_view, RecoveryPasswordView, \
    ConfirmRecoveryPasswordView
import time

urlpatterns = [
    path(f'signup/{int(time.time())}', SignUpView.as_view(), name='signup'),
    path(f'login/{int(time.time())}', LoginView.as_view(), name='login'),
    path(f'logout/{int(time.time())}', LogoutCustomView.as_view(), name='logout'),
    path(f'confirm_email/', ConfirmEmailPointView.as_view(), name='confirm_email'),
    path(f'confirm_email_message/', ConfirmEmailMessageView.as_view(), name='confirm_email_message'),
    path(f'warning_messages/{int(time.time())}', warning_messages_view, name='auth_messages'),
    path(f'allert/{int(time.time())}', AllertsView.as_view(), name='allert'),
    path('unique_username/', UniqueUserNameApiView.as_view(), name='check_for_unique_username'),
    path('unreg_auth_token/', UnregRegistrationApiView.as_view(), name='api-unreg-auth'),
    path(f'repair_password/{int(time.time())}', RecoveryPasswordView.as_view(), name='repair_password'),
    path(f'confirm_repair_password/', ConfirmRecoveryPasswordView.as_view(), name='repair_password_message'),
]
