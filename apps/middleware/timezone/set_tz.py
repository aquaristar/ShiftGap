import pytz

from django.utils import timezone


from apps.ui.models import UserProfile


class TimezoneMiddleware(object):

    def process_request(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
        return None


class SetUsersTimezoneMiddleware(object):

    def process_request(self, request):
        try:
            request.session['django_timezone'] = request.user.userprofile.timezone.zone
        except Exception:
            pass


# class ActivateUsersTimezoneFromProfileMiddleware(object):
#
#     def process_request(self, request):
#         import pdb
#         # pdb.set_trace()
#         try:
#             tz = request.user.userprofile.timezone
#             # request.session['django_timezone']
#             if tz:
#                 pdb.set_trace()
#                 timezone.activate(tz.zone)
#
#                 # pdb.set_trace()
#         except AttributeError:
#             timezone.deactivate()
#         return None