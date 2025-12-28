from django.db import models


class Employee(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Event(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('연차', '연차'),
        ('반차', '반차'),
        ('휴가', '휴가'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES)
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        return f"{self.employee} - {self.leave_type}"
