from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        # 모델 필드명과 정확히 일치합니다
        fields = ['employee', 'leave_type', 'start', 'end']

        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            # DateInput으로 변경하여 모델의 DateField와 형식을 맞춥니다.
            'start': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',  # 시간 없이 날짜만 선택하는 창으로 변경
            }),
            'end': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
