from django import forms
from django.core.exceptions import SuspiciousOperation
from django.contrib.auth.models import User

from apps.ui.models import UserProfile
from apps.organizations.views import OrganizationPermission
from .models import Shift, Schedule


class ShiftForm(forms.ModelForm):
    organization = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ShiftForm, self).__init__(*args, **kwargs)
        # FIXME organization could be changed from HTML form by malicious user
        self.fields['organization'].initial = self.request.user.userprofile.organization
        self.fields['user'].queryset = User.objects.filter(userprofile__organization=self.request.user.userprofile.organization)
        self.fields['schedule'].queryset = Schedule.objects.filter(organization=self.request.user.userprofile.organization)

    class Meta:
        model = Shift
        fields = ('start_time', 'end_time', 'user', 'schedule', 'organization')