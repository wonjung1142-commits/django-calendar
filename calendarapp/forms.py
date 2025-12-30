from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        # 필드 목록에 'employee'가 있다면 포함시켜야 합니다.
        # 만약 모델에 employee 필드가 없다면 아래 리스트에서 빼주세요.
        fields = ['employee', 'title', 'description', 'start_time', 'end_time']

        # 위젯 설정을 통해 HTML 입력창에 디자인 클래스를 입힙니다.
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-control',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '일정 제목 (예: 오후 근무)',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '메모사항을 입력하세요',
                'rows': 3,
            }),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',  # 스마트폰이나 브라우저에서 날짜/시간 선택기가 뜹니다.
            }, format='%Y-%m-%dT%H:%M'),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        # 모든 입력 필드에 'form-control' 클래스를 입혀서 부트스트랩 디자인을 적용합니다.
        for field in self.fields.values():
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs.update({'class': 'form-control'})
