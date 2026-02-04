from django.contrib import admin
from .models import Employee, Event


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    # 1. 목록에 표시할 필드 (직원, 휴가종류, 사용일)
    list_display = ('employee', 'leave_type', 'formatted_start_date')

    # 2. 우측 필터 바 (직원이름, 사용일로 분류)
    list_filter = ('employee', 'leave_type', 'start')

    # 3. 날짜 계층 구조 (상단에 연/월 선택 바 생성 - UI 핵심!)
    date_hierarchy = 'start'

    # 4. 검색창 (직원 이름으로 검색 가능)
    search_fields = ('employee__name',)

    # 5. 사용일 날짜 형식을 연/월/일로 표시하는 함수
    def formatted_start_date(self, obj):
        return obj.start.strftime('%Y/%m/%d')

    formatted_start_date.short_description = "사용일(연/월/일)"

    # UI 개선: 한 페이지에 표시할 개수 설정
    list_per_page = 20


# 어드민 페이지 상단 타이틀 변경 (UI 커스텀)
admin.site.site_header = "제일약국 관리자 포털"
admin.site.site_title = "제일약국 어드민"
admin.site.index_title = "약국 자동화 시스템 관리"
