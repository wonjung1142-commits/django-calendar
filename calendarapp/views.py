from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db.models import Q  # [중요] 날짜 겹침 계산을 위해 꼭 필요합니다!
from .models import Event, Employee
from .forms import EventForm


def calendar_view(request):
    """메인 캘린더 화면"""
    return render(request, 'calendarapp/calendar.html')


def event_list(request):
    """캘린더 데이터 API (날짜 겹침 문제 해결됨)"""
    start = request.GET.get('start')
    end = request.GET.get('end')

    # 1. 날짜 범위가 들어오면, 그 기간에 '걸쳐있는' 모든 일정을 찾습니다.
    if start and end:
        events = Event.objects.filter(
            # Case A: 종료일이 있는 일정 (기간 일정)
            (Q(end__isnull=False) & Q(start__lte=end) & Q(end__gte=start)) |
            # Case B: 종료일이 없는 일정 (하루 일정)
            (Q(end__isnull=True) & Q(start__lte=end) & Q(start__gte=start))
        )
    else:
        # 2. 날짜 범위가 없으면 안전하게 전체 데이터를 가져옵니다.
        events = Event.objects.all()

    data = []

    for event in events:
        # 색상 설정
        color = '#3788d8'  # 기본 파란색 (휴가/연차)
        if event.leave_type == '반차':
            color = '#f0ad4e'  # 오렌지색
        elif event.leave_type == '월차':
            color = '#5bc0de'  # 하늘색

        # 직원 정보가 삭제되었을 경우를 대비한 안전장치
        emp_name = event.employee.name if event.employee else "알수없음"

        data.append({
            'id': event.id,
            'title': f"{emp_name} ({event.leave_type})",
            'start': event.start.strftime('%Y-%m-%d'),
            # 종료일이 없으면 시작일과 동일하게 설정
            'end': event.end.strftime('%Y-%m-%d') if event.end else event.start.strftime('%Y-%m-%d'),
            'color': color,
            'extendedProps': {
                'isHoliday': True if event.leave_type == '휴가' else False
            }
        })
    return JsonResponse(data, safe=False)


@xframe_options_exempt
def apply_view(request):
    """신청 팝업 (iframe 허용)"""
    event_id = request.GET.get('edit')
    date_str = request.GET.get('date')
    instance = None

    # 수정 모드: 기존 데이터 가져오기
    if event_id:
        instance = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        # 삭제 버튼 처리
        if request.POST.get('delete') == '1' and instance:
            instance.delete()
            return render(request, 'calendarapp/apply.html', {'is_success': True})

        # 저장 버튼 처리
        form = EventForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return render(request, 'calendarapp/apply.html', {'is_success': True})
    else:
        # 초기값 설정 (날짜 클릭 시 해당 날짜 자동 입력)
        initial_data = {}
        if date_str:
            initial_data = {'start': date_str, 'end': date_str}
        form = EventForm(instance=instance, initial=initial_data)

    return render(request, 'calendarapp/apply.html', {
        'form': form,
        'is_edit': bool(instance)
    })


def employee_usage(request, employee_id):
    """직원별 휴가 사용 내역 (관리자용)"""
    employee = get_object_or_404(Employee, id=employee_id)

    # 연차, 반차, 월차 내역
    annual_half = Event.objects.filter(
        employee=employee,
        leave_type__in=['연차', '반차', '월차']
    ).order_by('-start')

    # 장기 휴가 내역
    long_leaves = Event.objects.filter(
        employee=employee,
        leave_type='휴가'
    ).order_by('-start')

    return render(request, 'calendarapp/employee_usage.html', {
        'employee': employee,
        'annual_half': annual_half,
        'leave': long_leaves
    })
