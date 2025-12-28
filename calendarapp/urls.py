from django.urls import path
from .views import calendar_view, event_list, apply_view, employee_usage

urlpatterns = [
    path('', calendar_view, name='calendar'),
    path('events/', event_list, name='event_list'),
    path('apply/', apply_view, name='apply'),

    path('employee/<int:employee_id>/', employee_usage, name='employee_usage'),

]
