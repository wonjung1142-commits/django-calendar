from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        # 모델의 필드명과 정확히 일치시켰습니다
        fields = ['employee', 'leave_type', 'start', 'end']

        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            # DateField 모델에 맞춰서 시간 입력을 뺀 DateInput을 사용합니다
            'start': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'end': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        # 모든 입력창에 부트스트랩 스타일을 적용합니다.
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
