import csv
import io
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q  # <--- 이 줄이 반드시 있어야 합니다!
from .models import MedicineMaster, MedicineLocation, MedicineStock


def inventory_list(request):
    q = request.GET.get('q', '')
    cabinet = request.GET.get('cabinet', '')
    show_all = request.GET.get('show_all', False)

    medicines = MedicineMaster.objects.all().select_related('location')

    if q:
        # Q 객체를 사용하여 더 정확한 검색을 수행합니다.
        medicines = medicines.filter(
            Q(name__icontains=q) | Q(code__icontains=q))

    if cabinet:
        medicines = medicines.filter(location__pos_number=cabinet)

    locations = MedicineLocation.objects.all().order_by('pos_number')

    return render(request, 'inventory/inventory_list.html', {
        'medicines_list': medicines if q or cabinet or show_all else [],
        'q': q,
        'selected_cabinet': cabinet,
        'locations': locations,
        'is_search': bool(q or cabinet or show_all)
    })


def medicine_upload(request):
    if request.method == "POST":
        csv_file = request.FILES.get('file')

        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, 'CSV 파일만 업로드 가능합니다.')
            return redirect('inventory:medicine_upload')

        try:
            data_set = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(data_set)
            reader = csv.DictReader(io_string)

            count = 0
            for row in reader:
                name = row.get('의약품명', '').strip()
                spec = row.get('규격', '').strip()
                code = row.get('보험코드', '').strip()
                loc_num = row.get('위치', '').strip()

                if not name:
                    continue

                location_obj, _ = MedicineLocation.objects.get_or_create(
                    pos_number=loc_num)

                MedicineMaster.objects.update_or_create(
                    name=name,
                    specification=spec,
                    location=location_obj,
                    defaults={'code': code}
                )
                count += 1

            messages.success(request, f'성공: {count}건의 약품 데이터가 반영되었습니다.')
            return redirect('inventory:inventory_list')
        except Exception as e:
            messages.error(request, f'에러 발생: {e}')
            return redirect('inventory:medicine_upload')

    return render(request, 'inventory/upload.html')  # 템플릿 파일이 있는지 확인하세요
