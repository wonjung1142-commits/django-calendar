from django.contrib import admin
from .models import MedicineLocation, MedicineMaster, MedicineStock

# 어드민 페이지 상단 명칭 변경
admin.site.site_header = "제일약국 재고관리 시스템"


@admin.register(MedicineLocation)
class MedicineLocationAdmin(admin.ModelAdmin):
    # 목록에 표시할 항목: 위치 번호, 상세 설명, 담당 직원
    list_display = ('pos_number', 'description', 'assigned_staff')
    # 검색 가능 필드
    search_fields = ('pos_number', 'description')
    # 담당 직원별 필터링
    list_filter = ('assigned_staff',)


@admin.register(MedicineMaster)
class MedicineMasterAdmin(admin.ModelAdmin):
    # 목록에 표시할 항목: 약품명, 규격, 보험코드, 위치
    list_display = ('name', 'specification', 'code', 'location')
    # 위치별 필터링
    list_filter = ('location',)
    # 약품명 또는 코드로 검색
    search_fields = ('name', 'code')
    # 한 페이지에 표시할 개수
    list_per_page = 50


@admin.register(MedicineStock)
class MedicineStockAdmin(admin.ModelAdmin):
    # 목록에 표시할 항목: 약품명, 유통기한, 재고량, 반품여부
    list_display = ('medicine', 'expiry_date', 'quantity',
                    'is_return_needed', 'updated_at')
    # 반품 필요 여부 및 유통기한별 필터링
    list_filter = ('is_return_needed', 'expiry_date')
    # 날짜별 계층 구조 (상단 연/월 바)
    date_hierarchy = 'expiry_date'
    # 수정 일자 순으로 정렬
    ordering = ('-updated_at',)

    # 재고가 0이하인 경우 강조하거나 반품이 필요한 경우 표시하는 로직 추가 가능
