from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from apps.organizations.models import OrganizationOwned, HasLocation


class Schedule(OrganizationOwned, HasLocation):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('location', 'name'),)


class ShiftManager(models.Manager):

    def publish(self, from_, to):
        # publish the shifts
        # FIXME
        return 'list_of_shifts_that_was_published'


class Shift(OrganizationOwned):
    schedule = models.ForeignKey(Schedule)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    user = models.ForeignKey('auth.User')
    published = models.BooleanField(default=False)
    twenty_four_hour_reminder_sent = models.BooleanField(default=False)
    ninety_minute_reminder_sent = models.BooleanField(default=False)
    user_has_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + ' from ' + str(self.start_time) + ' to ' + str(self.end_time)

    def start_date(self, request):
        # date as would be represented by the requesting users timezone
        return self.start_time.astimezone(tz=request.user.userprofile.timezone).date()

    def end_date(self, request):
        # date as would be represented by the requesting users timezone
        return self.end_time.astimezone(tz=request.user.userprofile.timezone).date()

    def clean(self):
        # Don't allow a start time to occur after an end time
        if self.start_time > self.end_time:
            raise ValidationError(_('Start time cannot occur after end time.'))

    def publish(self):
        # more good stuff will happen here eventually
        self.published = True
        self.save()

    def unpublish(self):
        self.published = False
        self.save()