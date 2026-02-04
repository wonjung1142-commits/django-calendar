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
