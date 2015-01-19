import json

from django.views.generic import ListView, CreateView, UpdateView
from django.http.response import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

import arrow
from rest_framework.generics import ListCreateAPIView
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

from apps.organizations.views import OrganizationOwnedRequired, UserProfileRequiredMixin, OrganizationPermission
from apps.ui.models import UserProfile
from .models import Shift, Schedule
from .forms import ShiftForm
from .serializers import ShiftSerializer


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

    def get_context_data(self, **kwargs):
        context = super(ShiftListView, self).get_context_data(**kwargs)
        return context


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
        ups = UserProfile.objects.filter(organization=self.request.user.userprofile.organization)
        employees = []
        for user in ups:
            employees.append({
                'name': user.user.username,
                'id': user.user.pk
            })
        context['employees'] = employees
        context['default_schedule'] = Schedule.objects.get(organization=self.request.user.userprofile.organization,
                                                           name='Default').pk
        return context


class ShiftCreateView(UserProfileRequiredMixin, ShiftBaseMixin, CreateView):
    pass


class ShiftUpdateView(OrganizationOwnedRequired, ShiftBaseMixin, UpdateView):
    pass


@login_required
@require_POST
def delete_shift_from_calendar(request):
    pk = request.POST['pk']
    try:
        shift = Shift.objects.get(pk=pk, organization=request.user.userprofile.organization)
    except Shift.DoesNotExist:
        raise Http404()

    shift.delete()
    response = {"response": "OK"}
    return HttpResponse(json.dumps(response))


class BelongsToOrganization(permissions.BasePermission):
    # FIXME review, currently non-functional
    def has_object_permission(self, request, view, obj):
        return obj.organization == request.user.userprofile.organization


class ShiftListCreateUpdateAPIView(ListCreateAPIView):
    serializer_class = ShiftSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    def get_queryset(self):
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        if start and end:
            start = arrow.get(start).floor('hour')
            end = arrow.get(end).ceil('hour')

            # FIXME account for timezone's in dates, floor and ceiling not enough

            return Shift.objects.filter(organization=self.request.user.userprofile.organization,
                                        start_time__gte=start.datetime, end_time__lte=end.datetime)
        else:
            return Shift.objects.filter(organization=self.request.user.userprofile.organization)