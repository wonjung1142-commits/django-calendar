import os
import sys
import django
import pandas as pd

# 1. 장고 환경 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


def upload_data():
    from inventory.models import MedicineMaster, MedicineLocation, MedicineStock

    # 파일명 고정 (업로드하신 파일명 기준)
    target_file = "약품위치.csv"

    if not os.path.exists(os.path.join(BASE_DIR, target_file)):
        print(f"❌ '{target_file}' 파일을 찾을 수 없습니다. 경로를 확인하세요.")
        return

    print(f"🔄 '{target_file}' 데이터를 Neon DB에 등록합니다...")

    try:
        # 기존 데이터 초기화 (깨끗한 상태에서 시작)
        MedicineStock.objects.all().delete()
        MedicineMaster.objects.all().delete()
        MedicineLocation.objects.all().delete()

        # CSV 읽기 (보험코드를 문자열로 읽어 지수 형태 방지)
        df = pd.read_csv(target_file, dtype={'보험코드': str})

        # 결측치 처리
        df['위치'] = df['위치'].fillna("미지정")
        df['규격'] = df['규격'].fillna("-")
        df['보험코드'] = df['보험코드'].fillna("")

        count = 0
        for _, row in df.iterrows():
            name = str(row['의약품명']).strip()
            spec = str(row['규격']).strip()
            pos_text = str(row['위치']).replace(" ", "").strip()
            code = str(row['보험코드']).strip()

            if not name or name == 'nan':
                continue

            # 2. 위치(MedicineLocation) 생성 또는 가져오기
            loc_obj, _ = MedicineLocation.objects.get_or_create(
                pos_number=pos_text)

            # 3. 약품 마스터(MedicineMaster) 생성
            med_obj, created = MedicineMaster.objects.get_or_create(
                name=name,
                specification=spec,
                location=loc_obj,
                defaults={'code': code}
            )

            # 4. 재고(MedicineStock) 연결
            if created:
                MedicineStock.objects.get_or_create(medicine=med_obj)
                count += 1

            if count % 500 == 0:
                print(f"⏳ {count}건 처리 완료...")

        print(f"✅ 성공: 총 {count}종의 약품이 Neon DB에 저장되었습니다!")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    upload_data()
