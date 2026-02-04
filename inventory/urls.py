from django.urls import path
from . import views

urlpatterns = [
    # 나중에 만들 약품 리스트 화면 주소입니다.
    path('', views.inventory_list, name='inventory_list'),
]
