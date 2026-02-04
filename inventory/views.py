import re
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import MedicineLocation, MedicineMaster, MedicineStock


def inventory_list(request):
    def natural_sort_key(s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', str(s))]

    # 1. POST 요청 처리 (추가 및 수정)
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

    # 3. 약장 번호 10단위 그룹화
    all_locs = MedicineLocation.objects.all()
    cabinet_nums = sorted({int(l.pos_number.split(
        '-')[0]) for l in all_locs if '-' in l.pos_number and l.pos_number.split('-')[0].isdigit()})

    cabinet_groups = {}
    for n in cabinet_nums:
        group_key = f"{(n-1)//10 * 10 + 1}~{(n-1)//10 * 10 + 10}번"
        if group_key not in cabinet_groups:
            cabinet_groups[group_key] = []
        cabinet_groups[group_key].append(str(n))

    sorted_medicines = sorted(
        list(medicines_qs), key=lambda x: natural_sort_key(x.location.pos_number))

    return render(request, 'inventory/inventory_list.html', {
        'medicines_list': sorted_medicines,
        'cabinet_groups': cabinet_groups,
        'selected_cabinet': selected_cabinet,
        'code_filter': code_filter,
        'q': q,
    })
