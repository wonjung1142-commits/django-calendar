from django.db import models


class MedicineLocation(models.Model):
    pos_number = models.CharField(
        max_length=50, unique=True, verbose_name="위치번호")

    def __str__(self):
        return self.pos_number


class MedicineMaster(models.Model):
    name = models.CharField(max_length=200, verbose_name="약품명")
    code = models.CharField(max_length=50, blank=True,
                            null=True, verbose_name="보험코드")
    specification = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="규격")
    location = models.ForeignKey(
        MedicineLocation, on_delete=models.SET_NULL, null=True, verbose_name="위치")

    def __str__(self):
        return self.name

# 이 모델이 없으면 500 에러가 날 수 있습니다.


class MedicineStock(models.Model):
    medicine = models.OneToOneField(
        MedicineMaster, on_delete=models.CASCADE, related_name='stock')
    quantity = models.IntegerField(default=0, verbose_name="재고수량")

    def __str__(self):
        return f"{self.medicine.name} 재고"
