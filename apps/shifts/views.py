from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from braces.views import LoginRequiredMixin

from apps.organizations.views import OrganizationOwnedRequired, UserProfileRequiredMixin, OrganizationPermission
from .models import Shift, Schedule
from .forms import ShiftForm


class ShiftBaseMixin(object):
    model = Shift
    form_class = ShiftForm

    def get_success_url(self):
        return '/'


class ShiftListView(UserProfileRequiredMixin, ShiftBaseMixin, ListView):
    # can't use organizationownedrequired with a list because no self.get_object()?

    def get_queryset(self):
        qs = super().get_queryset()
        return OrganizationPermission(self.request).filter_object_permissions(qs)


class ShiftCreateView(UserProfileRequiredMixin, ShiftBaseMixin, CreateView):
    pass


class ShiftUpdateView(OrganizationOwnedRequired, ShiftBaseMixin, UpdateView):
    pass