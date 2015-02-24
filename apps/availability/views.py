from django.shortcuts import render
from django.views.generic import ListView

from braces.views import LoginRequiredMixin

from .models import TimeOffRequest
from apps.organizations.views import OrganizationOwnedRequired, UserProfileRequiredMixin


class TimeOffRequestListingBaseMixin(object):
    model = TimeOffRequest

    def get_queryset(self):
        return TimeOffRequest.objects.filter(organization=self.request.user.userprofile.organization)


class TimeOffRequestListingForUser(UserProfileRequiredMixin, TimeOffRequestListingBaseMixin, ListView):
    template_name = 'availability/requests.html'