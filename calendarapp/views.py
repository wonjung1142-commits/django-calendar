from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from .models import Event, Employee
from .forms import EventForm


def calendar_view(request):
    """메인 캘린더 화면"""
    return render(request, 'calendarapp/calendar.html')


def event_list(request):
    """캘린더 데이터 API (수정됨)"""
    start = request.GET.get('start')
    end = request.GET.get('end')

    # [수정 포인트] start, end가 없으면 그냥 전체 데이터를 가져오도록 변경
    if start and end:
        events = Event.objects.filter(start__gte=start, start__lte=end)
    else:
        # 날짜 범위가 안 넘어오면 최근 1년치라도 가져오거나 전체를 가져옴
        # (혹은 그냥 전체 다 가져오기: 데이터가 많지 않으므로 안전함)
        events = Event.objects.all()

    data = []

    for event in events:
        color = '#3788d8'  # 기본(휴가)
        if event.leave_type == '반차':
            color = '#f0ad4e'
        elif event.leave_type == '월차':
            color = '#5bc0de'

        emp_name = event.employee.name if event.employee else "알수없음"

        data.append({
            'id': event.id,
            'title': f"{emp_name} ({event.leave_type})",
            'start': event.start.strftime('%Y-%m-%d'),
            # end 날짜가 없으면 start 날짜와 동일하게 설정 (FullCalendar 오류 방지)
            'end': event.end.strftime('%Y-%m-%d') if event.end else event.start.strftime('%Y-%m-%d'),
            'color': color,
            'extendedProps': {
                'isHoliday': True if event.leave_type == '휴가' else False
            }
        })
    return JsonResponse(data, safe=False)


@xframe_options_exempt  # 팝업 하얀 화면 방지
def apply_view(request):
    """신청 팝업 (iframe 허용)"""
    event_id = request.GET.get('edit')
    date_str = request.GET.get('date')
    instance = None

    if event_id:
        instance = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        # 삭제
        if request.POST.get('delete') == '1' and instance:
            instance.delete()
            return render(request, 'calendarapp/apply.html', {'is_success': True})

        # 저장
        form = EventForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return render(request, 'calendarapp/apply.html', {'is_success': True})
    else:
        # 초기값 설정
        initial_data = {}
        if date_str:
            initial_data = {'start': date_str, 'end': date_str}
        form = EventForm(instance=instance, initial=initial_data)

    return render(request, 'calendarapp/apply.html', {
        'form': form,
        'is_edit': bool(instance)
    })


def employee_usage(request, employee_id):
    """직원별 사용 내역"""
    employee = get_object_or_404(Employee, id=employee_id)
    annual_half = Event.objects.filter(employee=employee, leave_type__in=[
                                       '연차', '반차', '월차']).order_by('-start')
    long_leaves = Event.objects.filter(
        employee=employee, leave_type='휴가').order_by('-start')

    return render(request, 'calendarapp/employee_usage.html', {
        'employee': employee,
        'annual_half': annual_half,
        'leave': long_leaves
    })
