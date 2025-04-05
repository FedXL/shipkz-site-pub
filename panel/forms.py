from django import forms

from panel.models import OrdersGroup


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'Start Date'
        }),
        label='Start Date',
        required=True
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'End Date'
        }),
        label='End Date',
        required=True
    )


class GroupInfoForm(forms.ModelForm):
    class Meta:
        model = OrdersGroup
        fields = '__all__'


