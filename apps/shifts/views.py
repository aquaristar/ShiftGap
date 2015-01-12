from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse

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


class ShiftListCalendarView(ShiftListView):
    template_name = 'shifts/shift_calendar.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation to first get a context
        context = super(ShiftListCalendarView, self).get_context_data(**kwargs)
        events = []
        for shift in context['object_list']:
            events.append({
                # Fullcalendar.io uses 'title', 'start' and 'end'
                'title': str(shift.user),
                'start': str(shift.start_time.astimezone(self.request.user.userprofile.timezone)),
                'end': str(shift.end_time.astimezone(self.request.user.userprofile.timezone))
            })
        context['events'] = events
        return context


class ShiftCreateView(UserProfileRequiredMixin, ShiftBaseMixin, CreateView):
    pass


class ShiftUpdateView(OrganizationOwnedRequired, ShiftBaseMixin, UpdateView):
    pass