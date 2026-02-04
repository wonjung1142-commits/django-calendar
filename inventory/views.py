import re
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import MedicineLocation, MedicineMaster, MedicineStock


def inventory_list(request):
    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', str(s))]

    # 1. POST 요청 처리 (약품 추가 및 수정)
    if request.method == "POST":
        medicine_id = request.POST.get('medicine_id')
        medicine_name = request.POST.get('medicine_name')
        pos_number = request.POST.get(
            'pos_number', '').strip().replace(" ", "")
        insurance_code = request.POST.get('insurance_code', '').strip()
        quantity = request.POST.get('quantity') or 0

        try:
            location, _ = MedicineLocation.objects.get_or_create(
                pos_number=pos_number)
            if "(" in medicine_name:
                name = medicine_name.split("(")[0].strip()
                spec = medicine_name.split("(")[1].replace(")", "").strip()
            else:
                name = medicine_name.strip()
                spec = "기본"

            if medicine_id:
                medicine = MedicineMaster.objects.get(id=medicine_id)
                medicine.name, medicine.specification, medicine.location, medicine.code = name, spec, location, insurance_code
                medicine.save()
            else:
                medicine, _ = MedicineMaster.objects.get_or_create(
                    name=name, specification=spec, location=location, defaults={
                        'code': insurance_code}
                )
            MedicineStock.objects.update_or_create(
                medicine=medicine, defaults={'quantity': quantity})
        except Exception:
            pass
        return redirect('inventory:inventory_list')

    # 2. GET 요청 처리 (조회 및 필터)
    q = request.GET.get('q', '')
    selected_cabinet = request.GET.get('cabinet', '')
    code_filter = request.GET.get('code_filter', '')
    show_all = request.GET.get('show_all', '')

    # [핵심 수정] 검색/필터/전체보기가 없으면 빈 리스트로 시작 (로딩 속도 향상)
    if not (q or selected_cabinet or code_filter or show_all):
        medicines_list = []
    else:
        medicines_qs = MedicineMaster.objects.select_related('location').all()
        if q:
            medicines_qs = medicines_qs.filter(name__icontains=q)
        if code_filter == 'yes':
            medicines_qs = medicines_qs.exclude(
                Q(code='') | Q(code='0') | Q(code__isnull=True))
        elif code_filter == 'no':
            medicines_qs = medicines_qs.filter(
                Q(code='') | Q(code='0') | Q(code__isnull=True))

        if selected_cabinet:
            if selected_cabinet == "미지정":
                medicines_qs = [
                    m for m in medicines_qs if "미지정" in m.location.pos_number]
            else:
                medicines_qs = [m for m in medicines_qs if m.location.pos_number.startswith(
                    selected_cabinet + "-")]

        # 자연스러운 정렬 수행
        medicines_list = sorted(
            list(medicines_qs), key=lambda x: natural_sort_key(x.location.pos_number))

    # 3. 약장 그룹화 로직 (사이드바/상단 버튼용)
    all_locs = MedicineLocation.objects.all()
    cabinet_nums = []
    for l in all_locs:
        if '-' in l.pos_number:
            prefix = l.pos_number.split('-')[0]
            if prefix.isdigit():
                cabinet_nums.append(int(prefix))

    cabinet_nums = sorted(list(set(cabinet_nums)))

    cabinet_groups = {}
    for n in cabinet_nums:
        group_key = f"{(n-1)//10 * 10 + 1}~{(n-1)//10 * 10 + 10}번"
        if group_key not in cabinet_groups:
            cabinet_groups[group_key] = []
        cabinet_groups[group_key].append(str(n))

    return render(request, 'inventory/inventory_list.html', {
        'medicines_list': medicines_list,
        'cabinet_groups': cabinet_groups,
        'selected_cabinet': selected_cabinet,
        'code_filter': code_filter,
        'q': q,
        'is_search': bool(q or selected_cabinet or code_filter or show_all)
    })
