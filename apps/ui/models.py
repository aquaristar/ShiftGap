from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.organizations.models import Organization

from timezone_field import TimeZoneField


class UserProfile(models.Model):
    USER = 'USR'
    MANAGER = 'MGR'
    ADMINISTRATOR = 'ADM'
    USER_ROLES = (
        (USER, _('User')),
        (MANAGER, _('Manager')),
        (ADMINISTRATOR, _('Administrator'))
    )

    user = models.OneToOneField('auth.User')
    organization = models.ForeignKey(Organization)
    timezone = TimeZoneField()
    phone = models.CharField(max_length=25, blank=True)
    phone_reminders = models.BooleanField(default=True)
    phone_confirmed = models.BooleanField(default=False)
    role = models.CharField(max_length=3, choices=USER_ROLES, default=USER)

    def __str__(self):
        return _('Profile for ') + self.user.username