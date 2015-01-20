from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.shifts.tasks import new_shift_reminder
from .models import Shift


@receiver(post_save, sender=Shift, dispatch_uid="user_reminder")
def shift_saved(sender, **kwargs):
    # is it a new shift
    if kwargs.get('created'):
        print('This is a new shift.')
        new_shift_reminder.delay(shift_id=kwargs['instance'].pk)
    else:
        # Did the times change?
        # Did the user change?
        print('This was just updated')
    # is it an update