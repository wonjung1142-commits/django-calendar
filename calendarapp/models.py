from django.db import models


class Employee(models.Model):
    name = models.CharField(max_length=50, verbose_name="직원 성함")

    class Meta:
        # 어드민에 표시될 이름 설정
        verbose_name = "직원리스트"
        verbose_name_plural = "직원리스트"

    def __str__(self):
        return self.name


class Event(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('월차', '월차'),
        ('반차', '반차'),
        ('휴가', '휴가'),
    ]

    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, verbose_name="직원")
    leave_type = models.CharField(
        max_length=10, choices=LEAVE_TYPE_CHOICES, verbose_name="휴가 종류")
    start = models.DateField(verbose_name="사용일(시작)")
    end = models.DateField(verbose_name="사용일(종료)")

    class Meta:
        # 어드민에 표시될 이름 설정
        verbose_name = "휴가사용내역"
        verbose_name_plural = "휴가사용내역"

    def __str__(self):
        return f"{self.employee.name} - {self.leave_type}"
