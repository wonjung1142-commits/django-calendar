import csv
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import MedicineMaster, MedicineLocation, MedicineStock


def inventory_list(request):
    """약품 목록 조회 및 필터링"""
    q = request.GET.get('q', '')
    cabinet = request.GET.get('cabinet', '')
    code_filter = request.GET.get('code_filter', 'all')

    # 검색어나 약장 선택이 있을 때만 리스트를 가져와서 초기 로딩 속도 향상
    is_search = bool(q or cabinet)
    medicines = MedicineMaster.objects.all().select_related('location')

    if q:
        medicines = medicines.filter(
            Q(name__icontains=q) | Q(code__icontains=q))

    if cabinet:
        medicines = medicines.filter(location__pos_number=cabinet)

    # 보험코드 필터링 로직
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
    """약품 추가 및 수정 (AJAX 처리)"""
    if request.method == "POST":
        med_id = request.POST.get('med_id')
        name = request.POST.get('name')
        code = request.POST.get('code', '')
        spec = request.POST.get('spec', '')
        loc_num = request.POST.get('location', '미지정')

        # 위치 객체 처리
        location_obj, _ = MedicineLocation.objects.get_or_create(
            pos_number=loc_num)

        if med_id:  # 수정 로직
            medicine = get_object_or_404(MedicineMaster, id=med_id)
            medicine.name = name
            medicine.code = code
            medicine.specification = spec
            medicine.location = location_obj
            medicine.save()
        else:  # 신규 추가 로직
            MedicineMaster.objects.create(
                name=name, code=code, specification=spec, location=location_obj
            )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


def medicine_upload(request):
    """CSV 업로드 뷰 (기존 유지)"""
    if request.method == "POST":
        csv_file = request.FILES.get('file')
        if not csv_file:
            messages.error(request, '파일이 없습니다.')
            return redirect('inventory:medicine_upload')
        try:
            decoded_file = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            for row in reader:
                loc_obj, _ = MedicineLocation.objects.get_or_create(
                    pos_number=row.get('위치', '미지정'))
                MedicineMaster.objects.update_or_create(
                    name=row.get('의약품명'), specification=row.get('규격'),
                    location=loc_obj, defaults={'code': row.get('보험코드', '')}
                )
            messages.success(request, '업로드 성공')
            return redirect('inventory:inventory_list')
        except Exception as e:
            messages.error(request, f'에러: {e}')
    return render(request, 'inventory/upload.html')
