import requests
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Employee, Event
from .forms import EventForm


def get_korean_holidays(year):
    service_key = "G+gFhAr3MY2lFgSZK2/mwrW1FEJjYNxmPfuMiWWt8sPpebwPmq47a/tUuo7Ccc0fqn+6TD8+gYb6oGWbvsLpnw=="
    url = 'http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo'
    holidays = []
    params = {'serviceKey': service_key, 'solYear': year,
              'numOfRows': 100, '_type': 'json'}
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            res_data = response.json()
            items = res_data.get('response', {}).get(
                'body', {}).get('items', {}).get('item', [])
            if isinstance(items, dict):
                items = [items]
            for item in items:
                locdate = str(item['locdate'])
                date_obj = datetime.strptime(locdate, '%Y%m%d').date()
                holidays.append({'title': item['datename'], 'start': date_obj.isoformat(
                ), 'allDay': True, 'isHoliday': True, 'backgroundColor': 'transparent', 'textColor': '#d93025'})
    except:
        pass
    return holidays


def calendar_view(request):
    return render(request, 'calendarapp/calendar.html')


def event_list(request):
    start_str = request.GET.get('start', '')
    year = start_str.split('-')[0] if start_str else datetime.now().year
    holidays = get_korean_holidays(year)
    events = Event.objects.all()
    event_data = []
    for e in events:
        event_data.append({'id': e.id, 'title': f"{e.employee.name}({e.leave_type})", 'start': e.start.isoformat(), 'end': (
            e.end + timedelta(days=1)).isoformat(), 'allDay': True, 'color': '#1a73e8' if e.leave_type == '연차' else '#34a853'})
    return JsonResponse(holidays + event_data, safe=False)


def apply_view(request):
    date_str = request.GET.get('date')
    edit_id = request.GET.get('edit')
    event = get_object_or_404(Event, id=edit_id) if edit_id else None

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
        initial = {"start": date_str, "end": date_str} if date_str else {}
        form = EventForm(instance=event) if event else EventForm(
            initial=initial)
    return render(request, "calendarapp/apply.html", {"form": form, "is_edit": bool(event)})


def employee_usage(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    annual_half = Event.objects.filter(employee=employee, leave_type__in=[
                                       "연차", "반차"]).order_by('-start')
    leave = Event.objects.filter(
        employee=employee, leave_type="휴가").order_by('-start')
    return render(request, 'calendarapp/employee_usage.html', {'employee': employee, 'annual_half': annual_half, 'leave': leave})
