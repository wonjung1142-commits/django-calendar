from django.contrib import admin
from django.utils.timezone import now
from django.utils.safestring import mark_safe
from .models import Employee, Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('employee', 'display_leave_summary')
    list_filter = ('employee', 'leave_type', 'start')
    date_hierarchy = 'start'
    search_fields = ('employee__name',)

    def display_leave_summary(self, obj):
        # 해당 직원의 해당 월 모든 휴가 내역을 묶어서 표시
        leaves = Event.objects.filter(
            employee=obj.employee,
            start__year=obj.start.year,
            start__month=obj.start.month
        ).order_by('start')

        html = "".join(
            [f"<div style='margin-bottom:3px;'><b>{l.leave_type}</b> {l.start.strftime('%y. %m. %d')}</div>" for l in leaves])
        return mark_safe(html)

    display_leave_summary.short_description = "해당 월 사용 현황"

    def changelist_view(self, request, extra_context=None):
        # 처음 접속 시 이번 달(2026년 2월 등)로 자동 리다이렉트
        if 'start__year' not in request.GET and 'start__month' not in request.GET:
            current = now()
            q = request.GET.copy()
            q['start__year'] = str(current.year)
            q['start__month'] = str(current.month)
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super().changelist_view(request, extra_context=extra_context)


admin.site.site_header = "제일약국 관리자 포털"
