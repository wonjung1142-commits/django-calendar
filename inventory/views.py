import io
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from .models import MedicineMaster, MedicineLocation


def inventory_list(request):
    """약품 목록 조회"""
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

# 서버가 못 찾고 있는 함수가 바로 이겁니다! 꼭 포함되어야 합니다.


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
            MedicineMaster.objects.create(
                name=name, code=code, specification=spec, location=location_obj
            )

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
