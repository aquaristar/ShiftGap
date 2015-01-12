from django.db import models

from timezone_field import TimeZoneField


class Organization(models.Model):
    name = models.CharField(max_length=100)
    default_tz = TimeZoneField()

    def __str__(self):
        return self.name


class OrganizationOwned(models.Model):
    organization = models.ForeignKey(Organization)

    class Meta:
        abstract = True


class Location(OrganizationOwned):
    name = models.CharField(max_length=64)
    timezone = TimeZoneField()

    class Meta:
        unique_together = (('name', 'organization'),)


class HasLocation(models.Model):
    location = models.ForeignKey(Location)

    class Meta:
        abstract = True