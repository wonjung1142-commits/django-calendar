from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
# [중요] 여기는 inventory 앱이므로 MedicineMaster, MedicineLocation을 가져와야 합니다.
from .models import MedicineMaster, MedicineLocation


def inventory_list(request):
    """약품 목록 조회 (약장 그룹핑 기능 적용)"""
    q = request.GET.get('q', '')
    cabinet = request.GET.get('cabinet', '')  # 예: '1' (1번 약장 클릭 시)
    code_filter = request.GET.get('code_filter', 'all')

    is_search = bool(q or cabinet)
    medicines = MedicineMaster.objects.all().select_related('location')

    # 1. 검색어 필터
    if q:
        medicines = medicines.filter(
            Q(name__icontains=q) | Q(code__icontains=q))

    # 2. 약장 그룹 필터 (핵심!)
    if cabinet:
        # '1'번 약장을 선택하면 '1-1', '1-2', '1-3' 등 '1-'로 시작하는 모든 약을 찾음
        medicines = medicines.filter(
            location__pos_number__startswith=f"{cabinet}-")

    # 3. 보험코드 필터
    if code_filter == 'yes':
        medicines = medicines.exclude(
            Q(code='') | Q(code='0') | Q(code__isnull=True))
    elif code_filter == 'no':
        medicines = medicines.filter(
            Q(code='') | Q(code='0') | Q(code__isnull=True))

    # [핵심 로직] DB에 있는 위치(1-1, 1-2...)에서 앞번호(1)만 추출해서 목록 만들기
    all_locations = MedicineLocation.objects.values_list(
        'pos_number', flat=True)
    racks = set()
    for loc in all_locations:
        if loc and '-' in loc:
            # 하이픈(-) 앞의 숫자만 가져옴 (예: "1-1" -> "1")
            racks.add(loc.split('-')[0])

    # 숫자 순서대로 정렬 (1, 2, 3...)
    sorted_racks = sorted(
        list(racks), key=lambda x: int(x) if x.isdigit() else x)

    return render(request, 'inventory/inventory_list.html', {
        'medicines_list': medicines if is_search else [],
        'q': q,
        'selected_cabinet': cabinet,
        'racks': sorted_racks,  # 화면에 '1번 약장', '2번 약장' 버튼을 만들기 위해 보냄
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

        # 위치 정보 저장 (없으면 생성)
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
