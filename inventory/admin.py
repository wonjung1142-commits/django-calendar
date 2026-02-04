from django.contrib import admin
from .models import MedicineLocation, MedicineMaster


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
