from django.contrib import admin
from django.utils.timezone import now
from django.utils.safestring import mark_safe
from .models import Employee, Event


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name_tag',)
    search_fields = ('name',)

    def name_tag(self, obj):
        return mark_safe(f'<span style="background: #03cf5d; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold;">{obj.name}</span>')
    name_tag.short_description = "직원명"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('employee_tag', 'display_leave_summary')
    list_filter = ('employee', 'leave_type')
    date_hierarchy = 'start'

    def employee_tag(self, obj):
        return mark_safe(f'<b style="color: #333;">{obj.employee.name}</b>')
    employee_tag.short_description = "직원"

    def display_leave_summary(self, obj):
        try:
            leaves = Event.objects.filter(
                employee=obj.employee,
                start__year=obj.start.year,
                start__month=obj.start.month
            ).order_by('start')

            if obj.id != leaves.first().id:
                return mark_safe('<span style="color: #eee;">-</span>')

            html = ""
            for l in leaves:
                html += f'<div style="display:inline-block; background: #f8f9fa; border: 1px solid #ddd; padding: 6px 12px; border-radius: 12px; margin: 0 4px 4px 0;">' \
                        f'<span style="color: #03cf5d; font-weight: bold;">{l.leave_type}</span> {l.start.strftime("%m.%d")}</div>'
            return mark_safe(html)
        except:
            return "-"

    display_leave_summary.short_description = "이번 달 현황"

    def changelist_view(self, request, extra_context=None):
        if 'start__year' not in request.GET and 'start__month' not in request.GET:
            current = now()
            q = request.GET.copy()
            q['start__year'] = str(current.year)
            q['start__month'] = str(current.month)
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super().changelist_view(request, extra_context=extra_context)


admin.site.site_header = "제일약국 관리자 포털"
