from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        # 모델에 실제 존재하는 필드명인지 다시 한번 확인해주세요!
        # (만약 'employee'가 아니라 'user'라면 'user'로 바꿔야 합니다)
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
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
