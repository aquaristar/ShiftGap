import datetime

from django.shortcuts import render
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from django.http.response import JsonResponse
from django.core.exceptions import ValidationError, SuspiciousOperation
from django.contrib.auth.models import User

from .models import TimeOffRequest
from apps.organizations.views import OrganizationOwnedRequired, UserProfileRequiredMixin
from apps.ui.models import UserProfile


class TimeOffRequestListingBaseMixin(object):
    model = TimeOffRequest

    def get_queryset(self):
        return TimeOffRequest.objects.filter(organization=self.request.user.userprofile.organization)


def list_of_employees(request):
    # FIXME move to core app module, also has a ref in shifts/views.py ~106
    ups = UserProfile.objects.filter(organization=request.user.userprofile.organization)
    employees = []
    for user in ups:
            if user.user.first_name:
                name = user.user.first_name + ' ' + (user.user.last_name[0] if user.user.last_name else '')
                employees.append({
                    'name': name,
                    'id': user.user.pk
                })
            else:
                # fall back to using their username if no first_name in profile
                # FIXME: we need to require first_name for all accounts and remove this code
                employees.append({
                    'name': user.user.username,
                    'id': user.user.pk
                })
    return employees


class TimeOffRequestListing(UserProfileRequiredMixin, TimeOffRequestListingBaseMixin, ListView):
    template_name = 'availability/requests.html'

    def get_context_data(self, **kwargs):
        context = super(TimeOffRequestListing, self).get_context_data(**kwargs)
        context['users'] = list_of_employees(request=self.request)
        context['admin_or_manager'] = str(True if self.request.user.userprofile.admin_or_manager else False)
        if self.request.user.userprofile.admin_or_manager:
            context['pending'] = TimeOffRequest.objects.filter(organization=self.request.user.userprofile.organization,
                                                               status='P', start_date__gte=datetime.datetime.now().date())
            context['approved'] = TimeOffRequest.objects.filter(organization=self.request.user.userprofile.organization,
                                                                status='A', start_date__gte=datetime.datetime.now().date())
        return context

    def get_queryset(self):
        qs = super(TimeOffRequestListing, self).get_queryset()
        return qs.filter(user=self.request.user, start_date__gte=datetime.datetime.now().date()).order_by('start_date')


@require_POST
def submit_time_off_request(request):
    try:
        year, month, day = request.POST['start_date'].split('-')
        start_date = datetime.date(int(year), int(month), int(day))
        eyear, emonth, eday = request.POST['end_date'].split('-')
        end_date = datetime.date(int(eyear), int(emonth), int(eday))
        user = request.POST['user']
        note = request.POST.get('note', '')

    except ValueError:
        return JsonResponse({"result": "invalid data"}, status=400)

    # if not admin or manager, request must be for the user him or herself
    if not request.user.userprofile.admin_or_manager and request.user.pk != user:
        raise SuspiciousOperation

    time_off_request = TimeOffRequest(
        organization=request.user.userprofile.organization,
        start_date=start_date,
        end_date=end_date,
        user=User.objects.get(pk=user),
        request_note=note
    )

    try:
        time_off_request.clean()
        time_off_request.save()
        return JsonResponse({"result": "ok"})
    except ValidationError as e:
        return JsonResponse({"result": e.__str__()}, status=422)

@require_POST
def cancel_time_off_request(request):
    time_off_request = request.POST['request_pk']
    time_off_request = TimeOffRequest.objects.get(pk=time_off_request)
    if not request.user.userprofile.admin_or_manager and time_off_request.user != request.user:
        raise SuspiciousOperation
    else:
        time_off_request.cancel_away()
    return JsonResponse({"result": "ok"})

@require_POST
def approve_time_off_request(request):
    time_off_request = request.POST['request_pk']
    time_off_request = TimeOffRequest.objects.get(pk=time_off_request)
    # must be admin or manager
    if not request.user.userprofile.admin_or_manager:
        raise SuspiciousOperation
    else:
        time_off_request.approve()
    return JsonResponse({"result": "ok"})

@require_POST
def reject_time_off_request(request):
    time_off_request = request.POST['request_pk']
    time_off_request = TimeOffRequest.objects.get(pk=time_off_request)
    # must be admin or manager
    if not request.user.userprofile.admin_or_manager:
        raise SuspiciousOperation
    else:
        time_off_request.reject()
    return JsonResponse({"result": "ok"})