from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.clickjacking import xframe_options_exempt  # 팝업 차단 해제 도구
from .models import Event, Employee
from .forms import EventForm
from django.db.models import Count, Q


def calendar_view(request):
    """메인 캘린더 화면"""
    return render(request, 'calendarapp/calendar.html')


def event_list(request):
    """캘린더에 뿌려줄 데이터 (JSON)"""
    start = request.GET.get('start')
    end = request.GET.get('end')

    # 해당 기간의 데이터만 가져옴
    events = Event.objects.filter(start__gte=start, start__lte=end)
    data = []

    for event in events:
        color = '#3788d8'  # 기본 파란색 (연차 등)
        if event.leave_type == '반차':
            color = '#f0ad4e'  # 오렌지
        elif event.leave_type == '월차':
            color = '#5bc0de'  # 하늘색

        data.append({
            'id': event.id,
            'title': f"{event.employee.name} ({event.leave_type})",
            'start': event.start.strftime('%Y-%m-%d'),
            'end': event.end.strftime('%Y-%m-%d') if event.end else event.start.strftime('%Y-%m-%d'),
            'color': color,
            # 휴가인 경우 캘린더 날짜 색을 바꾸기 위한 플래그
            'extendedProps': {
                'isHoliday': True if event.leave_type == '휴가' else False
            }
        })
    return JsonResponse(data, safe=False)


@xframe_options_exempt  # [핵심] 이 줄이 있어야 팝업이 하얗게 안 나옵니다!
def apply_view(request):
    """팝업창 내용 (신청 폼)"""
    event_id = request.GET.get('edit')
    date_str = request.GET.get('date')
    instance = None

    # 수정 모드일 때 기존 데이터 가져오기
    if event_id:
        instance = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        # 삭제 버튼 눌렀을 때
        if request.POST.get('delete') == '1' and instance:
            instance.delete()
            return render(request, 'calendarapp/apply.html', {'is_success': True})

        # 저장 버튼 눌렀을 때
        form = EventForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            # 저장이 성공하면 팝업을 닫으라는 신호를 보냄
            return render(request, 'calendarapp/apply.html', {'is_success': True})
    else:
        # 처음 팝업 열 때 (날짜 클릭 시 해당 날짜 자동 입력)
        initial_data = {}
        if date_str:
            initial_data = {'start': date_str, 'end': date_str}

        form = EventForm(instance=instance, initial=initial_data)

    return render(request, 'calendarapp/apply.html', {
        'form': form,
        'is_edit': bool(instance)
    })


def employee_usage(request, employee_id):
    """직원별 휴가 사용 내역 (어드민용)"""
    employee = get_object_or_404(Employee, id=employee_id)

    # 연차/반차/월차 내역
    annual_half = Event.objects.filter(
        employee=employee,
        leave_type__in=['연차', '반차', '월차']
    ).order_by('-start')

    # 긴 휴가 내역
    long_leaves = Event.objects.filter(
        employee=employee,
        leave_type='휴가'
    ).order_by('-start')

    return render(request, 'calendarapp/employee_usage.html', {
        'employee': employee,
        'annual_half': annual_half,
        'leave': long_leaves
    })
