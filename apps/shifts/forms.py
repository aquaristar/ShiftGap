from django import forms

from .models import Shift, Schedule


class ShiftForm(forms.ModelForm):

    class Meta:
        model = Shift
        fields = ('start_time', 'end_time', 'user', 'schedule')