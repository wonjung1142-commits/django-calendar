from django.urls import path
from . import views

app_name = 'calendarapp'

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    # 이 줄이 있어야 캘린더에 일정이 뜹니다!
    path('list/', views.event_list, name='event_list'),
    path('apply/', views.apply_view, name='apply'),
    path('usage/<int:employee_id>/', views.employee_usage, name='employee_usage'),
]
