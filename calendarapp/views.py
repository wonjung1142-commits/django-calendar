import requests
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Employee, Event
from .forms import EventForm

# 1. 공공데이터포털 API를 통해 한국 공휴일을 가져오는 함수


def get_korean_holidays(year):
    # [주의] 본인의 서비스 키를 여기에 입력하세요
    service_key = "G+gFhAr3MY2lFgSZK2/mwrW1FEJjYNxmPfuMiWWt8sPpebwPmq47a/tUuo7Ccc0fqn+6TD8+gYb6oGWbvsLpnw=="
    url = 'http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo'

    holidays = []
    params = {
        'serviceKey': service_key,
        'solYear': year,
        'numOfRows': 100,
        '_type': 'json'
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            res_data = response.json()
            body = res_data.get('response', {}).get('body', {})
            if body and 'items' in body and body['items']:
                items = body['items'].get('item')
                if items:
                    if not isinstance(items, list):
                        items = [items]
                    for item in items:
                        locdate = str(item['locdate'])
                        holidays.append(datetime.strptime(
                            locdate, '%Y%m%d').strftime('%Y-%m-%d'))
    except Exception as e:
        print(f"API Error: {e}")
    return holidays

# 2. 메인 캘린더 화면 뷰


def calendar_view(request):
    return render(request, "calendarapp/calendar.html")

# 3. 일정 데이터를 JSON으로 반환하는 뷰 (직원 일정 + 공휴일)


def event_list(request):
    # 직원 근태 일정 가져오기
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
            "isHoliday": False,
        })

    # 공휴일 데이터 추가
    current_year = datetime.now().year
    holiday_dates = get_korean_holidays(current_year)

    for h_date in holiday_dates:
        data.append({
            "start": h_date,
            "allDay": True,
            "display": 'background',
            "backgroundColor": "transparent",
            "isHoliday": True,
        })

    return JsonResponse(data, safe=False)

# 4. 일정 등록 및 수정 뷰 (빠져있던 부분 추가)


def apply_view(request):
    date_str = request.GET.get("date")
    edit_id = request.GET.get("edit")
    event = None
    if edit_id:
        event = get_object_or_404(Event, id=edit_id)

    if request.method == "POST":
        if event and "delete" in request.POST:
            event.delete()
            return render(request, "calendarapp/apply.html", {"is_success": True})

        form = EventForm(
            request.POST, instance=event) if event else EventForm(request.POST)
        if form.is_valid():
            saved_event = form.save(commit=False)
            if saved_event.leave_type in ["연차", "반차"]:
                saved_event.end = saved_event.start
            saved_event.save()
            return render(request, "calendarapp/apply.html", {"is_success": True})
    else:
        if event:
            form = EventForm(instance=event)
        else:
            initial_data = {"start": date_str,
                            "end": date_str} if date_str else {}
            form = EventForm(initial=initial_data)

    return render(request, "calendarapp/apply.html", {"form": form, "is_edit": bool(event)})

# 5. 직원별 사용 내역 조회 뷰 (빠져있던 부분 추가)


def employee_usage(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    annual_half = Event.objects.filter(
        employee=employee,
        leave_type__in=["연차", "반차"]
    ).order_by("start")
    leave = Event.objects.filter(
        employee=employee,
        leave_type="휴가"
    ).order_by("start")

    return render(request, "calendarapp/employee_usage.html", {
        "employee": employee,
        "annual_half": annual_half,
        "leave": leave
    })
