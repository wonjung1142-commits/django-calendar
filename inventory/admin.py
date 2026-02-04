from django.contrib import admin
from .models import MedicineMaster, MedicineLocation, MedicineStock


@admin.register(MedicineMaster)
class MedicineMasterAdmin(admin.ModelAdmin):
    # 관리자 페이지 목록에 보일 항목들
    list_display = ('name', 'specification', 'get_location', 'code')
    search_fields = ('name', 'specification', 'location__pos_number')
    list_filter = ('location',)

    def get_location(self, obj):
        return obj.location.pos_number if obj.location else "-"
    get_location.short_description = '위치'


@admin.register(MedicineLocation)
class MedicineLocationAdmin(admin.ModelAdmin):
    list_display = ('pos_number', 'description')


@admin.register(MedicineStock)
class MedicineStockAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'expiry_date', 'quantity')
