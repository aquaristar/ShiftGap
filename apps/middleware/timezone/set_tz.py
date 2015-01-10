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


class ActivateUsersTimezoneFromProfileMiddleware(object):

    def process_request(self, request):
        try:
            tz = request.user.userprofile.timezone
            if tz:
                timezone.activate(tz)
            else:
                timezone.deactivate()
        except Exception:
            timezone.deactivate()