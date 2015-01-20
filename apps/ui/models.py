from django.db import models

from apps.organizations.models import Organization

from timezone_field import TimeZoneField


class UserProfile(models.Model):
    user = models.OneToOneField('auth.User')
    organization = models.ForeignKey(Organization)
    timezone = TimeZoneField()
    phone = models.CharField(max_length=25, blank=True)
    phone_reminders = models.BooleanField(default=True)

    def __str__(self):
        return 'Profile for ' + self.user.username