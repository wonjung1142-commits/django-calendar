# inventory/urls.py
from django.urls import path
from . import views

app_name = 'inventory'  # 이 줄이 반드시 있어야 합니다!

urlpatterns = [
    # name='inventory_list' 이 부분이 index.html의 이름과 일치해야 합니다.
    path('', views.inventory_list, name='inventory_list'),
]
