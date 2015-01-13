from django.db import models

import arrow

from apps.organizations.models import OrganizationOwned, HasLocation


class Schedule(OrganizationOwned, HasLocation):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('location', 'name'),)


class Shift(OrganizationOwned):
    schedule = models.ForeignKey(Schedule)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    user = models.ForeignKey('auth.User')

    def __str__(self):
        return self.user.username + ' from ' + str(self.start_time) + ' to ' + str(self.end_time)

    def start_date(self, request):
        # date as would be represented by the requesting users timezone
        return self.start_time.astimezone(tz=request.user.userprofile.timezone).date()

    def end_date(self, request):
        # date as would be represented by the requesting users timezone
        return self.end_time.astimezone(tz=request.user.userprofile.timezone).date()