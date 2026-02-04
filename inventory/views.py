import io
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
# MedicineStock이 models.py에 있다면 포함, 없다면 제거
from .models import MedicineMaster, MedicineLocation, MedicineStock


def inventory_list(request):
    """약품 목록 조회 (검색 최적화)"""
    q = request.GET.get('q', '')
    cabinet = request.GET.get('cabinet', '')
    code_filter = request.GET.get('code_filter', 'all')

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


def medicine_save(request):
    """약품 추가 및 수정 (AJAX)"""
    if request.method == "POST":
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
            # 재고 데이터 자동 생성 (에러 방지용)
            MedicineStock.objects.get_or_create(medicine=med)

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
