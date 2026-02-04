from django.http import HttpResponse


def inventory_list(request):
    return HttpResponse("<h1>테스트 성공!</h1> <p>이 화면이 보이면 서버는 정상입니다.</p>")
