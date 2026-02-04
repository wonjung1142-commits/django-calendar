import csv
import io
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .models import MedicineMaster, MedicineLocation, MedicineStock


def inventory_list(request):
    """약품 목록 조회 및 검색 기능"""
    q = request.GET.get('q', '')
    cabinet = request.GET.get('cabinet', '')
    show_all = request.GET.get('show_all', False)

    medicines = MedicineMaster.objects.all().select_related('location')

    if q:
        # 이름 또는 코드로 검색
        medicines = medicines.filter(
            Q(name__icontains=q) | Q(code__icontains=q))

    if cabinet:
        # 위치별 필터링
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
    """CSV 파일을 통한 약품 데이터 일괄 업로드"""
    if request.method == "POST":
        csv_file = request.FILES.get('file')

        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, 'CSV 형식의 파일만 업로드 가능합니다.')
            return redirect('inventory:medicine_upload')

        try:
            # [보강] 한글 인코딩 처리: UTF-8-SIG 시도 후 실패 시 CP949(윈도우 엑셀용) 시도
            try:
                decoded_file = csv_file.read().decode('utf-8-sig')
            except UnicodeDecodeError:
                csv_file.seek(0)
                decoded_file = csv_file.read().decode('cp949')

            io_string = io.StringIO(decoded_file)
            # DictReader를 사용하여 헤더 이름으로 데이터에 접근
            reader = csv.DictReader(io_string)

            count = 0
            for row in reader:
                # 엑셀 헤더 이름이 정확히 일치해야 합니다. (공백 제거 포함)
                name = row.get('의약품명', '').strip()
                spec = row.get('규격', '').strip()
                code = row.get('보험코드', '').strip()
                loc_num = row.get('위치', '').strip()

                if not name:
                    continue

                # 위치 정보가 없으면 생성, 있으면 가져옴
                location_obj, _ = MedicineLocation.objects.get_or_create(
                    pos_number=loc_num if loc_num else "미지정"
                )

                # 데이터 생성 또는 업데이트
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
            # 어떤 에러인지 화면에 구체적으로 표시
            messages.error(request, f'데이터 처리 중 에러 발생: {str(e)}')
            return redirect('inventory:medicine_upload')

    return render(request, 'inventory/upload.html')
