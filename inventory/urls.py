# inventory/urls.py
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    # 아래 줄이 빠져 있었습니다. 반드시 추가하세요!
    path('upload/', views.medicine_upload, name='medicine_upload'),
]
