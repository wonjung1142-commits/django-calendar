from django.db import models


class Employee(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Event(models.Model):
    # 명칭 변경: 연차 -> 월차
    LEAVE_TYPE_CHOICES = [
        ('월차', '월차'),
        ('반차', '반차'),
        ('휴가', '휴가'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES)
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        return f"{self.employee} - {self.leave_type}"
