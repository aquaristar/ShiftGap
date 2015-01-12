from django.db import models

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