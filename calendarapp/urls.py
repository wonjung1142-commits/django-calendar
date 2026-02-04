from django.urls import path
from .views import calendar_view, event_list, apply_view, employee_usage

# 이 줄이 있는지 확인하세요. 없으면 {% url 'calendarapp:...' %} 이 작동 안 합니다.
app_name = 'calendarapp'

urlpatterns = [
    path('', calendar_view, name='calendar'),
    path('events/', event_list, name='event_list'),
    path('apply/', apply_view, name='apply'),  # 반차 신청 경로
    path('employee/<int:employee_id>/', employee_usage, name='employee_usage'),
]
