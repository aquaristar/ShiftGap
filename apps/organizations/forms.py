from django import forms
from django.contrib.auth.models import User

from apps.ui.models import UserProfile
from .models import Organization


class OrganizationSetupForm(forms.ModelForm):

    class Meta:
        model = Organization
        fields = ('name', 'default_tz')


class UserSetupForm(forms.ModelForm):
    username = forms.CharField(max_length=30, min_length=5)
    password = forms.CharField(max_length=30, min_length=8)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(UserSetupForm, self).__init__(*args, **kwargs)

    class Meta:
        model = UserProfile
        fields = ('username', 'password', 'first_name', 'last_name', 'email', 'phone', 'phone_reminders', 'role')

    def save(self, commit=True):
        # create new user
        m = super(UserSetupForm, self).save(commit=False)
        user = User.objects.create_user(username=self.cleaned_data['username'], password=self.cleaned_data['password'],
                                 first_name=self.cleaned_data['first_name'], last_name=self.cleaned_data['last_name'],
                                 email=self.cleaned_data['email'])
        # populate missing UserProfile details before attempting save
        m.user = user
        m.organization = self.request.user.userprofile.organization
        m.timezone = self.request.user.userprofile.organization.default_tz
        if commit:
            m.save()
        return m


class UserSetupWithoutOrganizationForm(forms.ModelForm):
    organization_code = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(UserSetupWithoutOrganizationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = UserProfile
        fields = ('organization_code', 'phone', 'phone_reminders')

    def save(self, commit=True):
        m = super(UserSetupWithoutOrganizationForm, self).save(commit=False)
        m.user = self.request.user
        org = Organization.objects.get(pk=self.cleaned_data['organization_code'])
        m.organization = org
        m.timezone = org.default_tz
        if commit:
            m.save()
        return m