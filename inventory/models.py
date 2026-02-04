from django.db import models
from calendarapp.models import Employee


class MedicineLocation(models.Model):
    pos_number = models.CharField(
        max_length=50, unique=True, verbose_name="위치 번호")
    description = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="위치 상세")
    assigned_staff = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.pos_number


class MedicineMaster(models.Model):
    name = models.CharField(max_length=200, verbose_name="약품명")
    specification = models.CharField(max_length=100, verbose_name="규격")
    code = models.CharField(max_length=50, verbose_name="보험코드")
    # 위치 정보와 직접 연결 (에러 방지를 위해 null=True 추가)
    location = models.ForeignKey(
        MedicineLocation,
        on_delete=models.CASCADE,
        related_name='medicines',
        verbose_name="위치",
        null=True, blank=True
    )

    class Meta:
        unique_together = ('name', 'specification', 'location')

    def __str__(self):
        loc_name = self.location.pos_number if self.location else "위치미지정"
        return f"{self.name} ({self.specification}) - {loc_name}"


class MedicineStock(models.Model):
    medicine = models.ForeignKey(
        MedicineMaster, on_delete=models.CASCADE, related_name='stocks', verbose_name="약품정보")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="유통기한")
    quantity = models.IntegerField(default=0, verbose_name="재고량")
    is_return_needed = models.BooleanField(default=False, verbose_name="반품필요")
    updated_at = models.DateTimeField(auto_now=True)
