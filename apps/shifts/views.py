from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse

from braces.views import LoginRequiredMixin

from apps.organizations.views import OrganizationOwnedRequired, UserProfileRequiredMixin, OrganizationPermission
from .models import Shift, Schedule
from .forms import ShiftForm


class ShiftBaseMixin(object):
    model = Shift
    form_class = ShiftForm

    def get_success_url(self):
        return reverse('shifts:shift_list')

    def get_form_kwargs(self):
        kwargs = super(ShiftBaseMixin, self).get_form_kwargs()
        kwargs = kwargs.copy()
        kwargs['request'] = self.request
        return kwargs


class ShiftListView(UserProfileRequiredMixin, ShiftBaseMixin, ListView):
    # can't use organizationownedrequired with a list because no self.get_object()?

    def get_queryset(self):
        qs = super().get_queryset()
        return OrganizationPermission(self.request).filter_object_permissions(qs)


class ShiftCreateView(UserProfileRequiredMixin, ShiftBaseMixin, CreateView):

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save()
        return super(ShiftCreateView, self).form_valid(form)

    def form_invalid(self, form):
        return super(ShiftCreateView, self).form_invalid(form)


class ShiftUpdateView(OrganizationOwnedRequired, ShiftBaseMixin, UpdateView):
    pass