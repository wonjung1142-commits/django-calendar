import csv
import io
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import MedicineMaster, MedicineLocation, MedicineStock


def inventory_list(request):
    q = request.GET.get('q', '')
    cabinet = request.GET.get('cabinet', '')
    show_all = request.GET.get('show_all', False)

    # 위치 정보와 함께 약품 목록 가져오기
    medicines = MedicineMaster.objects.all().select_related('location')

    if q:
        # 약품명 또는 보험코드로 검색
        medicines = medicines.filter(
            name__icontains=q) | medicines.filter(code__icontains=q)
    if cabinet:
        # 선택한 약장 번호로 필터링
        medicines = medicines.filter(location__pos_number=cabinet)

    # 화면 하단 약장 버튼용 목록
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

        # CSV 파일 검증
        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(
                request, '엑셀에서 [CSV 쉼표로 분리] 형식으로 저장한 파일만 업로드 가능합니다.')
            return redirect('inventory:medicine_upload')

        try:
            # 엑셀 저장 방식에 따른 인코딩 처리 (utf-8-sig는 엑셀 한글 깨짐 방지용)
            data_set = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(data_set)
            # 엑셀의 헤더명을 키로 사용 (의약품명, 규격, 보험코드, 위치)
            reader = csv.DictReader(io_string)

            count = 0
            for row in reader:
                name = row.get('의약품명', '').strip()
                spec = row.get('규격', '').strip()
                code = row.get('보험코드', '').strip()
                loc_num = row.get('위치', '').strip()

                if not name:
                    continue  # 이름이 없으면 건너뜀

                # 1. 약장 위치(MedicineLocation) 생성 또는 가져오기
                location_obj, _ = MedicineLocation.objects.get_or_create(
                    pos_number=loc_num
                )

                # 2. 약품 마스터(MedicineMaster) 저장 또는 업데이트
                # 사용자가 정의한 unique_together (name, specification, location) 기준
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
            messages.error(request, f'파일 처리 중 오류가 발생했습니다: {str(e)}')
            return redirect('inventory:medicine_upload')

    return render(request, 'inventory/upload.html')
