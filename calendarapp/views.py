from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from .models import Event, Employee
from .forms import EventForm


def calendar_view(request):
    return render(request, 'calendarapp/calendar.html')


def event_list(request):
    # 복잡한 날짜 계산 다 빼고, 그냥 있는 거 다 가져옵니다.
    # 데이터가 100만 개가 아닌 이상 이 방식이 가장 안전하고 빠릅니다.
    events = Event.objects.all()

    data = []
    for event in events:
        color = "#57bc43"
        if event.leave_type == '반차':
            color = "#ed900f"
        elif event.leave_type == '월차':
            color = "#0088ff"

        emp_name = event.employee.name if event.employee else "알수없음"

        data.append({
            'id': event.id,
            'title': f"{emp_name} ({event.leave_type})",
            'start': event.start.strftime('%Y-%m-%d'),
            'end': event.end.strftime('%Y-%m-%d') if event.end else event.start.strftime('%Y-%m-%d'),
            'color': color,
            'extendedProps': {
                'isHoliday': True if event.leave_type == '휴가' else False
            }
        })
    return JsonResponse(data, safe=False)


@xframe_options_exempt
def apply_view(request):
    # 기존 코드 유지
    event_id = request.GET.get('edit')
    date_str = request.GET.get('date')
    instance = None

    if event_id:
        instance = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        if request.POST.get('delete') == '1' and instance:
            instance.delete()
            return render(request, 'calendarapp/apply.html', {'is_success': True})

        form = EventForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return render(request, 'calendarapp/apply.html', {'is_success': True})
    else:
        initial_data = {}
        if date_str:
            initial_data = {'start': date_str, 'end': date_str}
        form = EventForm(instance=instance, initial=initial_data)

    return render(request, 'calendarapp/apply.html', {
        'form': form,
        'is_edit': bool(instance)
    })


def employee_usage(request, employee_id):
    # 기존 코드 유지
    employee = get_object_or_404(Employee, id=employee_id)
    annual_half = Event.objects.filter(employee=employee, leave_type__in=[
                                       '연차', '반차', '월차']).order_by('-start')
    long_leaves = Event.objects.filter(
        employee=employee, leave_type='휴가').order_by('-start')
    return render(request, 'calendarapp/employee_usage.html', {
        'employee': employee, 'annual_half': annual_half, 'leave': long_leaves
    })
