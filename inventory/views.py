import csv
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
# MedicineStock이 없어도 에러가 안 나도록 제거하거나, models.py에 확실히 있다면 포함
from .models import MedicineMaster, MedicineLocation, MedicineStock


def inventory_list(request):
    """약품 목록 조회 (500 에러 방지 안전 모드)"""
    try:
        q = request.GET.get('q', '')
        cabinet = request.GET.get('cabinet', '')
        code_filter = request.GET.get('code_filter', 'all')

        # 검색 최적화
        is_search = bool(q or cabinet)
        medicines = MedicineMaster.objects.all().select_related('location')

        if q:
            medicines = medicines.filter(
                Q(name__icontains=q) | Q(code__icontains=q))
        if cabinet:
            medicines = medicines.filter(location__pos_number=cabinet)

        if code_filter == 'yes':
            medicines = medicines.exclude(
                Q(code='') | Q(code='0') | Q(code__isnull=True))
        elif code_filter == 'no':
            medicines = medicines.filter(
                Q(code='') | Q(code='0') | Q(code__isnull=True))

        locations = MedicineLocation.objects.all().order_by('pos_number')

        return render(request, 'inventory/inventory_list.html', {
            'medicines_list': medicines if is_search else [],
            'q': q,
            'selected_cabinet': cabinet,
            'locations': locations,
            'code_filter': code_filter,
            'is_search': is_search
        })

    except Exception as e:
        # 500 에러 대신 화면에 원인을 출력해주는 핵심 코드
        return render(request, 'inventory/inventory_list.html', {
            'error_message': f"시스템 오류 발생: {str(e)}",
            'medicines_list': [],
            'locations': []
        })


def medicine_save(request):
    """약품 추가/수정"""
    if request.method == "POST":
        try:
            med_id = request.POST.get('med_id')
            name = request.POST.get('name')
            code = request.POST.get('code', '')
            spec = request.POST.get('spec', '')
            loc_num = request.POST.get('location', '미지정')

            location_obj, _ = MedicineLocation.objects.get_or_create(
                pos_number=loc_num)

            if med_id:
                medicine = get_object_or_404(MedicineMaster, id=med_id)
                medicine.name = name
                medicine.code = code
                medicine.specification = spec
                medicine.location = location_obj
                medicine.save()
            else:
                med = MedicineMaster.objects.create(
                    name=name, code=code, specification=spec, location=location_obj
                )
                # 재고 객체도 같이 생성 (데이터 무결성 유지)
                MedicineStock.objects.get_or_create(medicine=med)

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error'}, status=400)
