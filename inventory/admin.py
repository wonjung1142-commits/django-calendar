from django.contrib import admin
from .models import MedicineLocation, MedicineMaster, MedicineStock

# 1. 약장 위치 관리 (에러 필드 제거)


@admin.register(MedicineLocation)
class MedicineLocationAdmin(admin.ModelAdmin):
    # description, assigned_staff 등 없는 필드 제거하고 '위치번호'만 남김
    list_display = ('pos_number',)
    search_fields = ('pos_number',)

# 2. 약품 마스터 관리 (유지)


@admin.register(MedicineMaster)
class MedicineMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'specification', 'code', 'location')
    list_filter = ('location',)
    search_fields = ('name', 'code')
    list_per_page = 50

# 3. 재고 관리 (에러 필드 제거)


@admin.register(MedicineStock)
class MedicineStockAdmin(admin.ModelAdmin):
    # expiry_date, is_return_needed 등 없는 필드 제거하고 '약품', '수량'만 남김
    list_display = ('medicine', 'quantity')
    # search_fields도 약품명으로만 단순화
    search_fields = ('medicine__name',)
