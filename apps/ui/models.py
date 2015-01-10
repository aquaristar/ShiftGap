import pytz
from django.db import models

from apps.organizations.models import Organization

from timezone_field import TimeZoneField


class UserProfile(models.Model):
    user = models.OneToOneField('auth.User')
    organization = models.ForeignKey(Organization)
    timezone = TimeZoneField()