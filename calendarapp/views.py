import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Employee, Event
from .forms import EventForm

# [공공데이터 API] 공휴일 가져오기 함수


def get_korean_holidays(year):
    # 서비스키는 발급받은 후 여기에 입력하세요. (현재는 예시 키)
    service_key = "YOUR_SERVICE_KEY_HERE"
    url = 'http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo'

    holidays = []
    for month in range(1, 13):
        params = {
            'serviceKey': service_key,
            'solYear': year,
            'solMonth': f"{month:02}",
            '_type': 'json'
        }
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                res_data = response.json()
                items = res_data.get('response', {}).get(
                    'body', {}).get('items', {}).get('item')
                if items:
                    if isinstance(items, list):
                        for item in items:
                            holidays.append(datetime.strptime(
                                str(item['locdate']), '%Y%m%d').strftime('%Y-%m-%d'))
                    else:
                        holidays.append(datetime.strptime(
                            str(items['locdate']), '%Y%m%d').strftime('%Y-%m-%d'))
        except:
            continue
    return holidays


def event_list(request):
    # 1. 직원 일정 가져오기
    events = Event.objects.select_related("employee")
    data = []
    LEAVE_COLORS = {"휴가": "#4CAF50", "연차": "#2196F3", "반차": "#FF9800"}

    for event in events:
        color = LEAVE_COLORS.get(event.leave_type, "#9E9E9E")
        data.append({
            "id": event.id,
            "title": f"{event.employee.name} · {event.leave_type}",
            "start": event.start.isoformat(),
            "end": (event.end + timedelta(days=1)).isoformat(),
            "allDay": True,
            "backgroundColor": color,
            "borderColor": "transparent",
            "isHoliday": False,  # 직원 일정은 공휴일 아님
        })

    # 2. 공휴일 가져오기 (현재 연도 기준)
    current_year = datetime.now().year
    holiday_dates = get_korean_holidays(current_year)

    for h_date in holiday_dates:
        data.append({
            "start": h_date,
            "allDay": True,
            "display": 'background',  # 화면에 블록 대신 배경/날짜 색상 제어용으로 사용
            "backgroundColor": "transparent",
            "isHoliday": True,  # JS에서 인식할 플래그
        })

    return JsonResponse(data, safe=False)

# 나머지 calendar_view, apply_view, employee_usage 함수는 동일하게 유지
