from django import forms

from .models import Organization


class OrganizationSetupForm(forms.ModelForm):

    class Meta:
        model = Organization
        fields = ('name', 'default_tz')