from __future__ import absolute_import

from django.conf import settings
from django.db import transaction
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from django_twilio.client import twilio_client

from shiftgap.celery import app


# FIXME move to core or phone
def send_phone_notifications(user_id):
    user = User.objects.get(pk=user_id)
    if user.userprofile.phone_confirmed and user.userprofile.phone_reminders and user.userprofile.phone_number:
        return True
    else:
        return False


# FIXME move to core or phone
def send_msg_to_user_if_allowed(user_id, message):
    user = User.objects.get(pk=user_id)
    if send_phone_notifications(user_id):
        msg = twilio_client.messages.create(
            body=message,
            to=user.userprofile.phone_number,
            from_=settings.TWILIO_DEFAULT_CALLERID
        )


@app.task
def notify_time_off_request_approved(request_id):
    from apps.availability.models import TimeOffRequest  # circular import
    req = TimeOffRequest.objects.get(pk=request_id)
    message = _('Hi %s, your request for time off starting on %s has been approved!' % (req.user.first_name,
                                                                                    str(req.start_date)))
    send_msg_to_user_if_allowed(req.user.pk, message=message)


@app.task
def notify_time_off_request_rejected(request_id):
    from apps.availability.models import TimeOffRequest  # circular import
    req = TimeOffRequest.objects.get(pk=request_id)
    message = _('Hi %s, your request for time off starting on %s has been rejected.' % (req.user.first_name,
                                                                                    str(req.start_date)))
    send_msg_to_user_if_allowed(req.user.pk, message=message)


@app.task
def notify_time_off_request_cancelled(request_id):
    from apps.availability.models import TimeOffRequest  # circular import
    req = TimeOffRequest.objects.get(pk=request_id)
    message = _('Hi %s, your request for time off starting on %s has been cancelled.' % (req.user.first_name,
                                                                                    str(req.start_date)))
    send_msg_to_user_if_allowed(req.user.pk, message=message)