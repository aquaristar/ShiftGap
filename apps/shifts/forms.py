import datetime

from django import forms
from django.contrib.auth.models import User
from django.db.models import QuerySet

import arrow

from apps.organizations.models import Organization
from .models import Shift, Schedule


class ShiftForm(forms.ModelForm):
    organization = forms.ModelChoiceField(queryset=Organization.objects.all(), widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ShiftForm, self).__init__(*args, **kwargs)
        # FIXME organization could be changed from HTML form by malicious user
        self.fields['organization'].initial = self.request.user.userprofile.organization
        self.fields['user'].queryset = User.objects.filter(userprofile__organization=self.request.user.userprofile.organization)
        self.fields['user'].initial = self.request.user
        self.fields['schedule'].queryset = Schedule.objects.filter(organization=self.request.user.userprofile.organization)
        self.fields['schedule'].initial = Schedule.objects.get(organization=self.request.user.userprofile.organization,
                                                               name='Default')
        self.fields['start_time'].initial = datetime.datetime.now()

    def save(self, commit=True):
        import pdb
        pdb.set_trace()
        self.organization = self.request.user.userprofile.organization
        return super(ShiftForm, self).save(commit=True)

    class Meta:
        model = Shift
        fields = ('start_time', 'end_time', 'user', 'schedule', 'organization')