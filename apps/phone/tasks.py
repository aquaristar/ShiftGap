import random

from django.db import transaction
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django_twilio.client import twilio_client

from apps.ui.models import UserProfile
from shiftgap.celery import app


@app.task
def send_user_phone_confirmation_code(user_id):
    with transaction.atomic():
        # generate a random code
        code = random.randint(9999, 99999)
        # save it to the user profile
        up = UserProfile.objects.get(user__pk=user_id)
        print(str(up))
        if up.phone_number and not up.phone_confirmed:
            up.phone_confirmation_code = code
            up.save()
            # send the code to the phone number
            message = _('Your ShiftGap activation code is %s') % str(code)
            msg = twilio_client.messages.create(
                body=message,
                to=up.phone_number,
                from_=settings.TWILIO_DEFAULT_CALLERID
            )