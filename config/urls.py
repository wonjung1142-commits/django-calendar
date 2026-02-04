from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

urlpatterns = [
    path('admin/', admin.site.urls),
    # 첫 접속 시 메뉴 선택 화면(index.html)을 보여줍니다.
    path('', lambda r: render(r, 'index.html'), name='home'),
    path('calendar/', include('calendarapp.urls')),
    path('inventory/', include('inventory.urls')),
]
