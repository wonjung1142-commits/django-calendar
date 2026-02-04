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

    target_file = None
    for file in os.listdir(BASE_DIR):
        if "약품위치" in file and (file.endswith('.csv') or file.endswith('.xlsx')):
            target_file = file
            break

    if not target_file:
        print("❌ '약품위치' 파일을 찾을 수 없습니다.")
        return

    print(f"🔄 '{target_file}' 데이터를 읽고 초기화 후 새로 등록합니다...")

    try:
        # 1. 기존 데이터 초기화 (이름/규격/위치 조합을 새로 맞추기 위해 싹 비웁니다)
        MedicineStock.objects.all().delete()
        MedicineMaster.objects.all().delete()
        MedicineLocation.objects.all().delete()

        if target_file.endswith('.csv'):
            df = pd.read_csv(target_file)
        else:
            df = pd.read_excel(target_file)

        df['위치'] = df['위치'].fillna("미지정")
        count = 0

        for _, row in df.iterrows():
            name = str(row['의약품명']).strip()
            spec = str(row['규격']).strip()
            # 위치 공백 제거 (1-1 형태로 통일)
            pos_text = str(row['위치']).replace(" ", "").strip()
            # 보험코드 처리 (0이나 NaN은 빈값으로)
            code = str(row['보험코드']).strip() if pd.notna(
                row['보험코드']) and str(row['보험코드']) != '0' else ""

            # 2. 위치(MedicineLocation) 생성 또는 가져오기
            loc_obj, _ = MedicineLocation.objects.get_or_create(
                pos_number=pos_text)

            # 3. 약품 마스터(MedicineMaster) 생성
            # [핵심] 이름, 규격, 위치를 모두 기준으로 삼아 하나라도 다르면 새로 만듭니다.
            med_obj, created = MedicineMaster.objects.get_or_create(
                name=name,
                specification=spec,
                location=loc_obj,
                defaults={'code': code}
            )

            # 4. 재고(MedicineStock) 연결
            # 엑셀에 동일한 [이름+규격+위치] 행이 여러 개 있어도 하나만 등록되게 처리
            if created:
                MedicineStock.objects.get_or_create(medicine=med_obj)
                count += 1

        print(f"✅ 총 {count}종의 약품(규격별 구분) 업로드 완료!")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    upload_data()
