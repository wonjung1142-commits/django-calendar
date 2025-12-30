from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        # apply.html 파일에 실제 존재하는 필드들로만 구성했습니다
        fields = ['employee', 'leave_type', 'start', 'end']

        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'start': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }, format='%Y-%m-%dT%H:%M'),
            'end': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        # 모든 입력창에 부트스트랩 스타일을 입힙니다.
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
