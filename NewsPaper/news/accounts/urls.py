from django.urls import path
from ..views import IndexView, upgrade_me


urlpatterns = [
    path('', IndexView.as_view(), name='account_view'),
    path('upgrade/', upgrade_me, name='account_upgrade'),
]