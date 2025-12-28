from .models import Employee
from datetime import datetime
from .forms import EventForm
from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Event


def event_list(request):
    events = Event.objects.all()

    data = []
    for event in events:
        data.append({
            "id": event.id,
            "title": event.leave_type,
            "start": event.start.isoformat(),
            "end": (event.end + timedelta(days=1)).isoformat(),
            "allDay": True,
        })

    return JsonResponse(data, safe=False)


def calendar_view(request):
    return render(request, "calendarapp/calendar.html")


def apply_view(request):
    date_str = request.GET.get('date')
    edit_id = request.GET.get('edit')

    event = None

    # ✅ 수정 모드일 때
    if edit_id:
        event = get_object_or_404(Event, id=edit_id)

    if request.method == 'POST':

        if event and 'delete' in request.POST:
            event.delete()
            return redirect('/')

        if event:
            # 기존 이벤트 수정
            form = EventForm(request.POST, instance=event)
        else:
            # 새 이벤트 생성
            form = EventForm(request.POST)

        if form.is_valid():
            saved_event = form.save(commit=False)

            # 연차/반차는 당일 처리
            if saved_event.leave_type in ['연차', '반차']:
                saved_event.end = saved_event.start

            saved_event.save()
            return redirect('/')

    else:
        if event:
            # 수정 모드 → 기존 값 채우기
            form = EventForm(instance=event)
        else:
            # 신규 모드
            initial_data = {}
            if date_str:
                initial_data = {
                    'start': date_str,
                    'end': date_str,
                }
            form = EventForm(initial=initial_data)

    return render(
        request,
        'calendarapp/apply.html',
        {
            'form': form,
            'is_edit': bool(event),
        }
    )


def employee_usage(request, employee_id):
    employee = Employee.objects.get(id=employee_id)

    annual_half = Event.objects.filter(
        employee=employee,
        leave_type__in=["연차", "반차"]
    ).order_by("start")

    leave = Event.objects.filter(
        employee=employee,
        leave_type="휴가"
    ).order_by("start")

    return render(
        request,
        "calendarapp/employee_usage.html",
        {
            "employee": employee,
            "annual_half": annual_half,
            "leave": leave,
        }
    )
