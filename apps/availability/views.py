import datetime

from django.shortcuts import render
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from django.http.response import JsonResponse
from django.core.exceptions import ValidationError
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
        return context


@require_POST
def submit_time_off_request(request):

    year, month, day = request.POST['start_date'].split('-')
    start_date = datetime.date(int(year), int(month), int(day))
    eyear, emonth, eday = request.POST['end_date'].split('-')
    end_date = datetime.date(int(eyear), int(emonth), int(eday))
    user = request.POST['user']

    if not request.user.userprofile.admin_or_manager and request.user.pk != user:
        raise PermissionError

    time_off_request = TimeOffRequest(
        organization=request.user.userprofile.organization,
        start_date=start_date,
        end_date=end_date,
        user=User.objects.get(pk=user)
    )
    # if not admin or manager, request must be for the user him or herself
    try:
        time_off_request.clean()
        time_off_request.save()
        return JsonResponse({"result": "ok"})
    except ValidationError as e:
        return JsonResponse(e.__str__())