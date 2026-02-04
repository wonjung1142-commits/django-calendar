from django.contrib import admin
from .models import MedicineLocation, MedicineMaster

# MedicineStock 관련 코드는 모두 삭제해야 합니다.


@admin.register(MedicineLocation)
class MedicineLocationAdmin(admin.ModelAdmin):
    list_display = ('pos_number',)
    search_fields = ('pos_number',)


@admin.register(MedicineMaster)
class MedicineMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'specification', 'code', 'location')
    list_filter = ('location',)
    search_fields = ('name', 'code')
    list_per_page = 50
