from django import forms

from .models import Run, RunInputFile


class RunCreateForm(forms.ModelForm):
    class Meta:
        model = Run
        fields = ["sample_sheet", "config", "target", "cores", "run_is_private", "args", "environment_variable"]


class InputFilesCreateForm(forms.ModelForm):
    class Meta:
        model = RunInputFile
        fields = ['input_data']
        widgets = {'input_data': forms.ClearableFileInput(attrs={'multiple': True}),}


