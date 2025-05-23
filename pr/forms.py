from django import forms
from .models import Budget

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['year', 'amount']
        widgets = {
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '2000',
                'max': '2100',
                'required': True
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'required': True
            })
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.full_clean()  # Выполняем валидацию
            instance.save()
        return instance 