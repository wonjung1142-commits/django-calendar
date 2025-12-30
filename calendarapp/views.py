# [전체 교체용 코드] calendarapp/views.py
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Employee, Event
from .forms import EventForm


def event_list(request):
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
            "borderColor": color,
        })
    return JsonResponse(data, safe=False)


def calendar_view(request):
    return render(request, "calendarapp/calendar.html")


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
            # 저장 후 팝업을 닫으라는 성공 신호를 보냅니다.
            return render(request, "calendarapp/apply.html", {"is_success": True})
    else:
        if event:
            form = EventForm(instance=event)
        else:
            initial_data = {"start": date_str,
                            "end": date_str} if date_str else {}
            form = EventForm(initial=initial_data)

    return render(request, "calendarapp/apply.html", {"form": form, "is_edit": bool(event)})


def employee_usage(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    annual_half = Event.objects.filter(employee=employee, leave_type__in=[
                                       "연차", "반차"]).order_by("start")
    leave = Event.objects.filter(
        employee=employee, leave_type="휴가").order_by("start")
    return render(request, "calendarapp/employee_usage.html", {"employee": employee, "annual_half": annual_half, "leave": leave})
