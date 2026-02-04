from django.contrib import admin
from django.utils.timezone import now
from django.utils.safestring import mark_safe
from .models import Employee, Event

# 1. 직원 명단 복구 (네이버 그린 스타일)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name_tag',)
    search_fields = ('name',)

    def name_tag(self, obj):
        return mark_safe(f'<span style="background: #03cf5d; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold;">{obj.name}</span>')
    name_tag.short_description = "직원명"

# 2. 휴가 사용 내역 (월별 요약 UI)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('employee_tag', 'display_leave_summary')
    list_filter = ('employee', 'leave_type')
    date_hierarchy = 'start'  # 상단 연/월 선택 바 유지

    def employee_tag(self, obj):
        return mark_safe(f'<b style="color: #1e1e1e; font-size: 0.95rem;">{obj.employee.name}</b>')
    employee_tag.short_description = "직원"

    def display_leave_summary(self, obj):
        # 해당 직원의 해당 월 모든 내역을 가져옴
        leaves = Event.objects.filter(
            employee=obj.employee,
            start__year=obj.start.year,
            start__month=obj.start.month
        ).order_by('start')

        # 중복 방지: 리스트의 첫 번째 행에서만 요약을 한꺼번에 보여줌
        if obj.id != leaves.first().id:
            return mark_safe('<span style="color: #eee;">-</span>')

        # 네이버 스타일의 둥근 박스 레이아웃
        html = ""
        for l in leaves:
            html += f'<div style="display:inline-block; background: #f8f9fa; border: 1px solid #e9ecef; ' \
                    f'padding: 7px 12px; border-radius: 12px; margin-right: 6px; margin-bottom: 4px; font-size: 0.85rem;">' \
                    f'<span style="color: #03cf5d; font-weight: bold;">{l.leave_type}</span> {l.start.strftime("%m.%d")}</div>'
        return mark_safe(html)

    display_leave_summary.short_description = "이번 달 사용 현황"

    def changelist_view(self, request, extra_context=None):
        # 처음 접속 시 자동으로 이번 달(2026년 2월) 필터링
        if 'start__year' not in request.GET and 'start__month' not in request.GET:
            current = now()
            q = request.GET.copy()
            q['start__year'] = str(current.year)
            q['start__month'] = str(current.month)
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super().changelist_view(request, extra_context=extra_context)


admin.site.site_header = "제일약국 관리자 포털"
