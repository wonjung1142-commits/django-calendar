from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from .models import MedicineMaster, MedicineLocation


def inventory_list(request):
    """약품 목록 조회 (약장 그룹핑 적용)"""
    q = request.GET.get('q', '')
    cabinet = request.GET.get('cabinet', '')  # 이제 '1-1'이 아니라 '1'이 들어옵니다.
    code_filter = request.GET.get('code_filter', 'all')

    is_search = bool(q or cabinet)
    medicines = MedicineMaster.objects.all().select_related('location')

    # 1. 검색어 필터
    if q:
        medicines = medicines.filter(
            Q(name__icontains=q) | Q(code__icontains=q))

    # 2. 약장 버튼 필터 (핵심 변경!)
    if cabinet:
        # '1'번 약장을 누르면 '1-'로 시작하는 모든 위치(1-1, 1-2...)를 찾습니다.
        medicines = medicines.filter(
            location__pos_number__startswith=f"{cabinet}-")

    # 3. 보험코드 필터
    if code_filter == 'yes':
        medicines = medicines.exclude(
            Q(code='') | Q(code='0') | Q(code__isnull=True))
    elif code_filter == 'no':
        medicines = medicines.filter(
            Q(code='') | Q(code='0') | Q(code__isnull=True))

    # [핵심 로직] 존재하는 모든 위치에서 '1', '2' 같은 앞자리만 추출해서 중복 제거
    all_locations = MedicineLocation.objects.values_list(
        'pos_number', flat=True)
    racks = set()
    for loc in all_locations:
        if loc and '-' in loc:
            # "1-1" -> "1"만 추출
            racks.add(loc.split('-')[0])

    # 숫자 순서대로 정렬 (1, 2, 3...)
    sorted_racks = sorted(
        list(racks), key=lambda x: int(x) if x.isdigit() else x)

    return render(request, 'inventory/inventory_list.html', {
        'medicines_list': medicines if is_search else [],
        'q': q,
        'selected_cabinet': cabinet,
        'racks': sorted_racks,  # locations 대신 racks를 보냅니다.
        'code_filter': code_filter,
        'is_search': is_search
    })


def medicine_save(request):
    """약품 추가 및 수정 (기존 코드 유지)"""
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
