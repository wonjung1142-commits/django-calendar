from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    # path('upload/', views.medicine_upload ... ) <-- 이 줄을 과감히 지우세요!
    path('save/', views.medicine_save, name='medicine_save'),
]
