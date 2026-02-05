from django.http import HttpResponse


def inventory_list(request):
    """500 에러 원인 추적용 긴급 진단 뷰"""
    try:
        # 1. models.py 파일 자체를 불러와 봅니다.
        from . import models

        # 2. 모델 파일 안에 'MedicineMaster'(약품) 클래스가 있는지 확인합니다.
        if not hasattr(models, 'MedicineMaster'):
            return HttpResponse("""
                <h1 style='color:red;'>🚨 [비상] models.py 파일 오류!</h1>
                <h3>inventory/models.py 파일에 'MedicineMaster'가 없습니다.</h3>
                <p>혹시 캘린더용 models.py(Event, Employee)가 여기에 덮어씌워졌나요?</p>
                <p>-> <b>inventory/models.py</b>를 약품용 코드로 다시 복구해야 합니다.</p>
            """)

        # 3. 모델이 있다면, 실제 DB 연결을 시도해봅니다.
        from .models import MedicineMaster, MedicineLocation
        med_count = MedicineMaster.objects.count()
        loc_count = MedicineLocation.objects.count()

        return HttpResponse(f"""
            <h1 style='color:green;'>✅ 모델과 DB는 정상입니다!</h1>
            <h3>현재 데이터: 약품 {med_count}개, 위치 {loc_count}개</h3>
            <p>이 화면이 보인다면, models.py는 안전합니다.</p>
            <p>이제 <b>views.py의 로직(오타나 들여쓰기)</b>만 다시 점검하면 됩니다.</p>
        """)

    except Exception as e:
        # 그 외의 에러가 나면 상세 내용을 화면에 뿌립니다.
        import traceback
        error_msg = traceback.format_exc()
        return HttpResponse(f"""
            <h1 style='color:red;'>🔥 에러 발생 (이 내용을 보여주세요)</h1>
            <pre style='background:#f4f4f4; padding:15px; border:1px solid #ccc;'>{error_msg}</pre>
        """)


def medicine_save(request):
    return HttpResponse("진단 모드입니다.")
