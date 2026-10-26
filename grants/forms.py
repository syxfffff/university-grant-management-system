from django import forms
from django.utils import timezone
from .models import Application, Decision


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["title", "abstract", "amount"]
        widgets = {"abstract": forms.Textarea(attrs={"rows": 7})}

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount > self.instance.call.max_amount:
            raise forms.ValidationError("Requested amount exceeds the call limit.")
        return amount

    def clean(self):
        data = super().clean()
        call = self.instance.call
        if not call.is_open or call.deadline < timezone.localdate():
            raise forms.ValidationError("This call is closed.")
        return data


class DecisionForm(forms.ModelForm):
    class Meta:
        model = Decision
        fields = ["outcome", "feedback"]
        widgets = {"feedback": forms.Textarea(attrs={"rows": 5})}
