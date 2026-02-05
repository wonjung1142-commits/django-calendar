from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from .models import MedicineMaster, MedicineLocation


def inventory_list(request):
    """약품 목록 조회 (약장 그룹핑 + 안전한 정렬 적용)"""
    q = request.GET.get('q', '')
    cabinet = request.GET.get('cabinet', '')
    code_filter = request.GET.get('code_filter', 'all')

    # 검색어가 있거나 약장을 선택했을 때만 검색 모드
    is_search = bool(q or cabinet)
    medicines = MedicineMaster.objects.all().select_related('location')

    # 1. 검색어 필터
    if q:
        medicines = medicines.filter(
            Q(name__icontains=q) | Q(code__icontains=q))

    # 2. 약장 그룹 필터
    if cabinet:
        # '1'번 선택 -> '1-1', '1-2' 등 찾기
        medicines = medicines.filter(
            location__pos_number__startswith=f"{cabinet}-")

    # 3. 보험코드 필터
    if code_filter == 'yes':
        medicines = medicines.exclude(
            Q(code='') | Q(code='0') | Q(code__isnull=True))
    elif code_filter == 'no':
        medicines = medicines.filter(
            Q(code='') | Q(code='0') | Q(code__isnull=True))

    # [핵심 로직] 약장 번호 추출 (1-1 -> 1)
    all_locations = MedicineLocation.objects.values_list(
        'pos_number', flat=True)
    racks = set()
    for loc in all_locations:
        if loc and '-' in loc:
            racks.add(loc.split('-')[0])

    # [수정됨] 500 에러 방지용 안전한 정렬 로직
    # 숫자는 숫자대로(1, 2, 10), 문자는 문자대로(A, B) 정렬
    sorted_racks = sorted(list(racks), key=lambda x: (
        0, int(x)) if x.isdigit() else (1, x))

    return render(request, 'inventory/inventory_list.html', {
        'medicines_list': medicines if is_search else [],
        'q': q,
        'selected_cabinet': cabinet,
        'racks': sorted_racks,
        'code_filter': code_filter,
        'is_search': is_search
    })


def medicine_save(request):
    """약품 추가 및 수정"""
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
