from os import environ
import arrow

from django.utils import timezone

from apps.shifts.models import Shift


def process_ui_views(request):
    return {'build': environ.get('BUILD_HASH', None),
            'time': arrow.utcnow().datetime,
            'naive': timezone.is_aware(arrow.utcnow().datetime),
            'yourtz': request.session.get('django_timezone', None),
            'myshifts': Shift.objects.published_upcoming(user=request.user)[0:10]
    }