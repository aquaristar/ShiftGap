from datetime import timedelta

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

import arrow

from apps.organizations.models import OrganizationOwned, HasLocation


class Schedule(OrganizationOwned, HasLocation):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('location', 'name'),)


class ShiftManager(models.Manager):

    def list_shifts(self, user):
        """
        Returns a list of all for a users organization
        :param user:
        :return: list of shifts
        """
        shifts = self.all()
        if user.is_authenticated():
            try:
                up = user.userprofile
                shifts = shifts.filter(organization_id=up.organization_id)
            except AttributeError:
                shifts = shifts.none()
        return shifts

    def published(self, user):
        shifts = self.all()
        if user.is_authenticated():
            try:
                up = user.userprofile
                shifts = shifts.filter(organization_id=up.organization_id, published=True)
            except AttributeError:
                shifts = shifts.none()
        return shifts

    def published_upcoming(self, user):
        shifts = self.published(user=user)
        if shifts:
            shifts = shifts.filter(start_time__gte=arrow.utcnow().datetime).order_by('start_time')
        return shifts

    def unpublished(self, user):
        shifts = self.all()
        if user.is_authenticated():
            try:
                up = user.userprofile
                shifts = shifts.filter(organization_id=up.organization_id, published=False)
            except AttributeError:
                shifts = shifts.none()
        return shifts

    def unpublished_upcoming(self, user):
        shifts = self.unpublished(user=user)
        if shifts:
            shifts = shifts.filter(start_time__gte=arrow.utcnow().datetime).order_by('start_time')
        return shifts


class Shift(OrganizationOwned):
    schedule = models.ForeignKey(Schedule)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    user = models.ForeignKey('auth.User')
    published = models.BooleanField(default=False)
    twenty_four_hour_reminder_sent = models.BooleanField(default=False)
    ninety_minute_reminder_sent = models.BooleanField(default=False)
    user_has_confirmed = models.BooleanField(default=False)

    objects = ShiftManager()

    def __str__(self):
        return self.user.username + ' ' + _('from') + ' ' + str(self.start_time) + ' ' + _('to') + ' ' + str(self.end_time)

    @property
    def duration(self):
        duration = (self.end_time - self.start_time)
        duration = duration / timedelta(hours=1)
        # FIXME this may fail around DST transitions, we need to calculate duration as it would
        # be experienced by the user in his or her timezone - actually wait? these are in UTC so we're good?
        # return str(divmod(duration.days * 86400 + duration.seconds, 60))
        return duration

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


