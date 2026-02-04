from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('upload/', views.medicine_upload, name='medicine_upload'),
    path('save/', views.medicine_save, name='medicine_save'),  # 추가/수정 경로
]
