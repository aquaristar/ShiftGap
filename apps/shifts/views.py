import json

from django.views.generic import ListView, CreateView, UpdateView, TemplateView, FormView
from django.http.response import HttpResponse, Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages


import arrow
from rest_framework.generics import ListCreateAPIView, ListAPIView, GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

from apps.organizations.views import OrganizationOwnedRequired, UserProfileRequiredMixin, OrganizationPermission
from apps.ui.models import UserProfile
from .models import Shift, Schedule
from .forms import ShiftForm, PublishShiftDateRangeForm
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
    template_name = 'shifts/shift_list.html'
    # can't use organizationownedrequired with a list because no self.get_object()?
    from_ = None
    to = None

    def get_queryset(self):
        qs = super().get_queryset()

        # filter by date range if selected
        from_ = self.request.GET.get('from', None)
        to = self.request.GET.get('to', None)
        if from_ and to:
            import datetime
            start = datetime.datetime.strptime(from_, '%Y-%m-%d')
            end = datetime.datetime.strptime(to, '%Y-%m-%d')

            start = self.request.user.userprofile.timezone.localize(start)
            start = arrow.get(start).floor('day')
            start = start.datetime
            end = self.request.user.userprofile.timezone.localize(end)
            end = arrow.get(end)
            end = end.ceil('day').datetime
        else:
            end = arrow.now(tz=self.request.user.userprofile.timezone).replace(days=7)
            end = end.ceil('day')
            start = arrow.now(tz=self.request.user.userprofile.timezone).floor('day')
            start = start.datetime
            end = end.datetime

        self.from_ = start
        self.to = end
        qs = qs.filter(start_time__gte=start, end_time__lte=end, published=True).order_by('start_time')
        return OrganizationPermission(self.request).filter_object_permissions(qs)

    def get_context_data(self, **kwargs):
        context = super(ShiftListView, self).get_context_data(**kwargs)
        context['from'] = self.from_
        context['to'] = self.to
        if self.request.GET.get('byuser', None):
            context['byuser'] = True
        return context


class ShiftListForUserView(ShiftListView):

    def get_queryset(self):
        qs = super(ShiftListForUserView, self).get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs


class ShiftListCalendarView(UserProfileRequiredMixin, TemplateView):
    template_name = 'shifts/shift_calendar.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation to first get a context
        context = super(ShiftListCalendarView, self).get_context_data(**kwargs)
        ups = UserProfile.objects.filter(organization=self.request.user.userprofile.organization)
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
        context['employees'] = employees
        context['default_schedule'] = Schedule.objects.get(organization=self.request.user.userprofile.organization,
                                                           name='Default').pk
        return context


class ShiftCreateView(UserProfileRequiredMixin, ShiftBaseMixin, CreateView):
    pass


class ShiftUpdateView(OrganizationOwnedRequired, ShiftBaseMixin, UpdateView):
    pass


# FIXME move to core
class AdminOrManagerRequiredMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.userprofile.admin_or_manager:
            raise Http404()
        else:
            return super().dispatch(request, *args, **kwargs)


# FIXME move to core or utils module
def date_range_to_datetime_helper(start_date, end_date, timezone):
    '''
    Provides a helper function for getting proper datetime ranges from user submitted
    start date to end date.
    :param start_date: start date in format YYYY-MM-DD
    :param end_date:  end date in format YYYY-MM-DD
    :param timezone: must be a timezone object
    :return: start, end
    '''
    import datetime
    import arrow
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    start = timezone.localize(start)
    start = arrow.get(start).floor('day').datetime
    end = timezone.localize(end)
    end = arrow.get(end)
    end = end.ceil('day').datetime
    # FIXME add 3 hours to end to approximate shifts that actually end the next day but
    # for most accounting purposes are meant to be the same day
    return start, end


class ShiftPublishFormView(UserProfileRequiredMixin, AdminOrManagerRequiredMixin, FormView):
    template_name = 'shifts/shift_publish_range.html'
    form_class = PublishShiftDateRangeForm

    def form_valid(self, form):
        start_datetime, end_datetime =\
            date_range_to_datetime_helper(start_date=form.cleaned_data['from_date'],
                                                                     end_date=form.cleaned_data['to_date'],
                                                                     timezone=self.request.user.userprofile.timezone)

        shifts = Shift.objects.filter(start_time__gte=start_datetime, end_time__lte=end_datetime,
                                      organization=self.request.user.userprofile.organization,
                                      published=False)
        for shift in shifts:
            shift.publish()
        messages.info(self.request, "You just published %d shifts" % int(shifts.count()))
        return HttpResponseRedirect(reverse('shifts:shift_calendar'))


class ShiftUnpublishFormView(ShiftPublishFormView):

    def form_valid(self, form):
        start_datetime, end_datetime =\
            date_range_to_datetime_helper(start_date=form.cleaned_data['from_date'],
                                                                     end_date=form.cleaned_data['to_date'],
                                                                     timezone=self.request.user.userprofile.timezone)

        shifts = Shift.objects.filter(start_time__gte=start_datetime, end_time__lte=end_datetime,
                                      organization=self.request.user.userprofile.organization,
                                      published=True)
        for shift in shifts:
            shift.unpublish()
        messages.info(self.request, "You just unpublished %d shifts" % int(shifts.count()))
        return HttpResponseRedirect(reverse('shifts:shift_calendar'))


# FIXME: move to core module
from django.contrib.auth.decorators import user_passes_test


def admin_or_manager(user):
    return True if user.userprofile.admin_or_manager else False

@login_required
@require_POST
@user_passes_test(admin_or_manager)
def delete_shift_from_calendar(request):
    pk = request.POST['pk']
    try:
        shift = Shift.objects.get(pk=pk, organization=request.user.userprofile.organization)
    except Shift.DoesNotExist:
        raise Http404()

    shift.delete()
    response = {"response": "OK"}
    return HttpResponse(json.dumps(response))

@login_required
@require_POST
@user_passes_test(admin_or_manager)
def publish_unpublish_single_shift(request):
    pk = request.POST['pk']
    # pub = True if request.POST['pub'] == 'True' else False
    pub = request.POST.get('pub', None)
    pub = pub.lower()
    if pub == 'true':
        pub = True
    else:
        pub = False
    try:
        shift = Shift.objects.get(pk=pk, organization=request.user.userprofile.organization)
    except Shift.DoesNotExist:
        raise Http404()
    shift.publish() if pub else shift.unpublish()
    response = {"response": "OK"}
    return HttpResponse(json.dumps(response))


# ################################## API VIEWS ################################## #

class BelongsToOrganization(permissions.BasePermission):
    # FIXME review, currently non-functional
    def has_object_permission(self, request, view, obj):
        return obj.organization == request.user.userprofile.organization


class ShiftListAPIMixin(object):
    serializer_class = ShiftSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    def get_queryset(self):
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        if start and end:
            start = arrow.get(start).floor('day')
            end = arrow.get(end).ceil('day')

            # FIXME account for timezone's in dates, floor and ceiling not enough
            return Shift.objects.filter(organization=self.request.user.userprofile.organization,
                                        start_time__gte=start.datetime, end_time__lte=end.datetime)
        else:
            return Shift.objects.filter(organization=self.request.user.userprofile.organization)


class ShiftListCreateUpdateAPIView(ShiftListAPIMixin, ListCreateAPIView):

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(published=True)
        return qs

    def create(self, request, *args, **kwargs):
        # only managers can create shifts
        if not request.user.userprofile.admin_or_manager:
            result = {"result": "permission denied"}
            return HttpResponse(json.dumps(result))
        else:
            return super(ShiftListCreateUpdateAPIView, self).create(request, *args, **kwargs)




class ShiftListFilteredAPIView(ShiftListAPIMixin, ListAPIView):

    def get_queryset(self):
        queryset = super(ShiftListFilteredAPIView, self).get_queryset()
        # filter by user
        user = self.request.query_params.get('user', None)
        if user:
            queryset = queryset.filter(user__pk=user, published=True)

        # filter by schedule
        schedule = self.request.query_params.get('schedule', None)
        if schedule:
            queryset = queryset.filter(schedule__pk=schedule)
        return queryset


class ShiftListUnpublishedAPIView(ShiftListAPIMixin, ListAPIView):

    def get_queryset(self):
        queryset = super(ShiftListUnpublishedAPIView, self).get_queryset()
        # only management should be able to see unpublished shifts
        if self.request.user.userprofile.admin_or_manager:
            queryset = queryset.filter(published=False)
        return queryset

from django.views.decorators.csrf import csrf_exempt


class ShiftUpdateAPIView(UpdateModelMixin, GenericAPIView):
    serializer_class = ShiftSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (TokenAuthentication, SessionAuthentication,)

    def dispatch(self, request, *args, **kwargs):
        # Admin or manager is required
        if not request.user.userprofile.admin_or_manager:
            raise Http404()
        return super(ShiftUpdateAPIView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # I give up on PUT and PATCH
        return self.partial_update(request, *args, **kwargs)

    def get_queryset(self):
        qs = Shift.objects.filter(pk=self.request.data['pk'], organization=self.request.user.userprofile.organization)
        return qs


        # def spawn_worker(request):
        #     import sys
        #     import subprocess
        #     subprocess.Popen(["celery", "worker", "--app=shiftgap.celery"])
        #     return HttpResponseRedirect('/')
        # This is just some test code to see how heroku would react with
        # requests that are > 30 seconds.
        # import time
        # from django.http import StreamingHttpResponse
        #
        # def something_to_check():
        #     pass
        #
        # def stream_response(request):
        #     something_to_check = True
        #     resp = StreamingHttpResponse(stream_response_generator())
        #     something_to_check = False
        #     return resp
        #
        # def stream_response_generator():
        #     for x in range(1, 300):
        #         if something_to_check():
        #             yield '{} <br /> {}'.format(x, ' '*1)
        #         else:
        #             return
        #         time.sleep(1)