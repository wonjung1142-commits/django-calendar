from django.contrib import admin
from .models import Employee, Event   # ✅ 둘 다 import

admin.site.register(Employee)
admin.site.register(Event)
