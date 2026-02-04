from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # medicine_upload 줄이 있으면 절대 안 됩니다! 지워주세요.
    path('', views.inventory_list, name='inventory_list'),
    path('save/', views.medicine_save, name='medicine_save'),
]
