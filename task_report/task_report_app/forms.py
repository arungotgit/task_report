from django import forms
from .models import TaskFile

class TaskAdminForm(forms.ModelForm):
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = TaskFile
        fields = '__all__'



