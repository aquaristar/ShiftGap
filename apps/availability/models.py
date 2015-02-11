from datetime import time, datetime, date, timedelta
import pytz
import itertools

from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from apps.organizations.models import OrganizationOwned


class TimeOffRequest(OrganizationOwned):
    """
    Represents a user's request for time off and manages the status of the request and creating the
    associated Availability record.
    """
    CHOICES = (
        ('P', _('Pending')),
        ('A', _('Approved')),
        ('R', _('Rejected')),
        ('C', _('Cancelled'))
    )

    start_date = models.DateField()
    end_date = models.DateField()
    user = models.ForeignKey('auth.User')
    approved = models.BooleanField(default=False)
    status = models.CharField(max_length=1, choices=CHOICES, default='P')
    availability = models.ForeignKey('availability.Availability', blank=True, null=True, on_delete=models.SET_NULL)
    request_note = models.CharField(max_length=128, blank=True)

    @property
    def days_approved(self):
        if self.status == 'A':
            time_delta = (self.end_date - self.start_date).days + 1
            return time_delta
        else:
            return 0

    @property
    def days_rejected(self):
        if self.status == 'R':
            time_delta = (self.end_date - self.start_date).days + 1
            return time_delta
        else:
            return 0

    @property
    def days_cancelled(self):
        if self.status == 'C':
            time_delta = (self.end_date - self.start_date).days + 1
            return time_delta
        else:
            return 0

    def clean(self):
        # end date must not be before start date
        if self.end_date < self.start_date:
            raise ValidationError(_("End time cannot be before start time."))

    def approve(self):
        # Approve the request for time off and create an associated Availability record to reflect that
        # the employee will not be present for the given dates.
        with transaction.atomic():
            self.approved = True
            self.status = 'A'

            # create availability record to note the time away so that the user doesn't get scheduled
            av = Availability(
                user=self.user,
                organization=self.organization,
                start_date=self.start_date,
                end_date=self.end_date,
                approved=True
            )
            av.save(approved=True)  # to mark as approved otherwise save method defaults to False on any changes
            self.availability = av
            self.save()

            day_count = (self.end_date - self.start_date).days + 1
            days_of_week = set()

            # we only want to create _one_ DayAvailability record for each day of the week so let's find out
            # what days are represented in the range start_date to end_date inclusive (so we use a set)
            for single_date in (self.start_date + timedelta(days=n) for n in range(day_count)):
                days_of_week.add(single_date.weekday())

                # once we already have all 7 days we don't need to continue anymore
                if len(days_of_week) == 7:
                    break

            for day in days_of_week:
                av.create_day_availability_record(day_of_week=day,
                                                  start_time=time(0, 0, 0), end_time=time(0, 0, 0))

    def reject(self):
        with transaction.atomic():
            self.approved = False
            self.status = 'R'
            self.save()

    def cancel_away(self):
        # reverse the time away operation
        self.status = 'C'
        if self.availability:
            self.availability.delete()
        self.save()


# Issue: Maintain employee availability in a simple yet complete way.
#
#   Note: Any time the employee is scheduled this will be queried to make sure they are
#        available so we must keep efficiency in mind
#       Will also implementing highlighting of shifts that are in violation of this availability
#       so viewing a calendar of shifts each shift will be queried against this table
#
#
# General Availability:
#     This is the availability that will be used if there is no other specific availability
#     - Monday to Saturday any time after 12 PM
#     - Daily from 9am to 8pm
#
#
# Special Life Event Availability
#     e.g. final University exams
#     - From March 1st to March 20th available Thursday to Saturday after 2 PM and Monday after 6pm
#
#
# Doctors Appointment
#     - June 1st available from 12 PM to 1:30 PM and from 4pm to end of day
#
#
# Time off
#     (for time off a distinct db table will be used just including it here for reference)
#     - Away from June 15th to June 28th (assume inclusive)
#
#
# Also all availability needs to be approved by a manager
# unless org settings say to default all to approved

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


class AvailabilityManager(models.Manager):

    def is_user_available(self, user, date_, start_time, end_time):
        # Given a user, date and time, query if the user is available to work or not
        pass

    def check_shift(self, shift):
        """
        Given a shift, return True if there are no availability conflicts and False if there are conflicts

        Note: a user always sets their availability in reference to their own timezone. Because we store
        Availability ranges as dates and DayAvailability ranges as times (not datetimes), we cannot reliably
        store this data in UTC. So in checking for conflicts, we first must convert the start_time and end_time
        of the shift to the users timezone for accurate results (since we store it in the database as UTC).

        This can be refactored
        """
        start_time = shift.start_time.astimezone(tz=shift.user.userprofile.timezone)
        end_time = shift.end_time.astimezone(tz=shift.user.userprofile.timezone)
        shift_date = start_time.date() if start_time.date() == end_time.date() else None

        # The code below works for both cases, this commented out code works if the start_time and end_time
        # are on the same day.
        # if shift_date:
        #     # hurray the shift is on a single date from the users perspective and we only need to reference
        #     # a single availability record
        #     av = self.get_availability_for_date(user=shift.user, av_date=shift_date)
        #
        #     # if no availability record is present, we return True and assume the user is availabile
        #     if av is None:
        #         return True
        #     if av.datetime_is_in_range(start_time) and av.datetime_is_in_range(end_time):
        #         # if the shift start_time and end_time is within the Availability period or
        #         # no Availability record exists
        #         return True
        #     return False
        # else:
        # The shift spans more than one day (from the perspective of the user's timezone) so
        # we need to reference two potential availability records (they could be the same)

        av1 = self.get_availability_for_date(user=shift.user, av_date=start_time.date())
        av2 = self.get_availability_for_date(user=shift.user, av_date=end_time.date())

        # if both None then we assume the user is available so we return True
        if av1 is None and av2 is None:
            return True

        # if two availability records
        if av1 and av2:
            if av1.datetime_is_in_range(start_time) and av2.datetime_is_in_range(end_time):
                return True
        elif av1:
            # if just av1 is present then we're only bound by the single Availability record
            if av1.datetime_is_in_range(start_time):
                return True
        elif av2:
            # if just av2 is present then we're only bound by the single Availability record
            if av2.datetime_is_in_range(end_time):
                return True
        return False

    def get_availability_for_date(self, user, av_date):
        # we want to ignore anything that hasn't yet been approved
        av = self.filter(approved=True)
        # see if there is any availability records that correspond for the specific date
        av = av.filter(user=user, start_date__lte=av_date, end_date__gte=av_date)

        if av.exists():
            return av[0]  # only one record should ever exist matching this query
        else:
            # if none then see if there are any general availability records for the user
            av = self.filter(user=user, start_date=None, end_date=None)
            if av.exists():
                return av[0]  # only one record should ever exist matching this query
            else:
                # create a blank availability record here????
                # if none then return None (we assume the user is always available with this set)
                return None


class Availability(OrganizationOwned):
    """
    Represents a date range when an employee is available to work.

    start_date
    end_date
        Refers to specific periods of time the availability is in effect for
        If BLANK or Null - then we assume it's 'general' or day to day availability and is in
        effect for all times not represented by an Availability instance with
        start_date and end_date set. Only one blank/null record per user can exist.
    user
        Who the availability is for

    If there is a related DayAvailability record for the day of the week belonging to this
    Availability instance, then we use that availability information. If there isn't, then we
    assume they are just available.


    Important - for DayAvailability records, they have only times and not dates. We must join them
    with the dates here (start_date and end_date) then translate the datetime object into the users
    timezone to provide them with meaningful data.

    """
    start_date = models.DateField(blank=True, null=True)  # if blank/null we assume this is the users 'general'
    end_date = models.DateField(blank=True, null=True)    # availability aka 'day to day' availability
    user = models.ForeignKey('auth.User')

    approved = models.BooleanField(default=False)  # requires manager approval before coming into effect

    objects = AvailabilityManager()

    class Meta:
        unique_together = (('start_date', 'user'), ('end_date', 'user'), ('start_date', 'end_date', 'user'),)

    def __str__(self):
        return _('Availability for: %s') % self.user.username

    @property
    def expired(self):
        # if end_date is past, return True else return False
        # can be used to purge the database of old availability records
        # availability_date = self.user.userprofile.timezone.localize(datetime.now())
        # end_date = self.user.userprofile.timezone.localize(datetime.combine(self.end_date, datetime.now().time()))

        # This is basic hackish as different users around the world will experience different expiry
        # so we'll just compare in UTC and add a time delta of 1 day to be reasonably sure it's actually
        # expired
        return True if datetime.now().date() > (self.end_date + timedelta(days=1)) else False

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, approved=False):
        # if modified, we need to get approval again
        if not approved:
            self.approved = False  # unless we're explicitly called approve()
        return super(Availability, self).save()

    def approve(self):
        """
        Organizations typically want to approve their employees new availability before it comes into effect.
        @TODO - an auto approval mechanism based on Organization settings
        """
        self.approved = True
        self.save(approved=True)  # must call with approved=True , see save() method

    def clean(self):
        # FIXME - move to pre_save signal?
        # Only one record can exist per User that has the 'start_date' and 'end_date' that is null
        # otherwise we won't know which record is the users 'general' or day to day availability
        if not self.start_date and not self.end_date:
            if self.pk and Availability.objects.filter(user=self.user, start_date=None, end_date=None).count() > 1:
                raise ValidationError(_('Only only general availability record is permitted. Edit the existing record.'))
            elif not self.pk and Availability.objects.filter(user=self.user,
                                                             start_date=None, end_date=None).count() > 0:
                raise ValidationError(_('Only only general availability record is permitted. Edit the existing record.'))

        def test_overlap(dt1_st, dt1_end, dt2_st, dt2_end):
            return dt1_st <= dt2_end and dt1_end >= dt2_st

        # ignore if no start_date and end_date set
        if self.start_date and self.end_date:
            # Goal: Make sure two Availability instances don't exist with overlapping ranges
            availabilities = Availability.objects.filter(user=self.user).exclude(start_date=None, end_date=None)

            # put all of your intervals in one array
            av_list = list(availabilities)
            # we assume it's not saved yet to the database if self.pk is None
            if self.pk is None:  # if it's not saved yet we still need to take the current range into account
                av_list += [self]

            # sort the array by the lower bound of each interval, then the upper bound
            av_list = sorted(av_list, key=lambda x: (x.start_date, x.end_date))

            avs = len(av_list)
            # Loop through the intervals from lowest lower bound to highest upper bound:
            for avx in range(0, avs):

                try:
                    # If the interval after this one starts before this one ends,
                    # raise a validation error
                    overlap = test_overlap(av_list[avx].start_date, av_list[avx].end_date,
                                           av_list[avx+1].start_date, av_list[avx+1].end_date)
                    if overlap:
                        raise ValidationError(_('Date ranges cannot overlap.'))
                except IndexError:
                    pass

        # start date must be before end date
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError(_('Start date is invalid, start date must be before end date.'))
        return super(Availability, self).clean()

    def create_day_availability_record(self, day_of_week, start_time=None, end_time=None):
        DayAvailability.objects.create(
            availability=self,
            day_of_week=day_of_week,
            start_time=start_time or time.min,
            end_time=end_time or time.max
        )

    def reset_daily_availability(self):
        for day in self.dayavailability_set.all():
            day.delete()
        self.clean()
        self.save()

    def datetime_is_in_range(self, av_date):
        # find the day of the week
        # see if there's a DayAvailability instance
        weekday = av_date.weekday()

        # if within range of at least one DayAvailability record return True
        # if not within range of at least one DayAvailability record return False
        if self.dayavailability_set.filter(day_of_week=weekday).exists():
            # do stuff
            for day in self.dayavailability_set.filter(day_of_week=weekday):
                if day.start_time <= av_date.time() <= day.end_time:
                    return True
            else:
                # av_date not within at least one range so user is not available to work
                return False
        else:
            # no DayAvailability records exists for this day of the week, so we assume the user is available
            return True


class DayAvailability(models.Model):
    """
    Represents the availability for the user for a specific day of the week
    Multiple DayAvailability records can exist for the same day of the week
    e.g. Monday from 9am to 12pm then from 6 pm to 9 pm

    `availability`
        Related availability record.

    `day_of_week`
        Day of the week availability is for, in python datetime 0 is Monday and 6 is Sunday
            Note: in javascript 0 is Sunday, 6 is Saturday!!

    `start_time`
    `end_time`
        Time range the user is available to work
    """
    CHOICES = (
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    )

    availability = models.ForeignKey('availability.Availability')
    day_of_week = models.PositiveIntegerField(max_length=1, choices=CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    @property
    def day(self):
        return self.CHOICES[self.day_of_week]  # FIXME this probably doesn't work

    def __str__(self):
        return 'DayAvailability for ' + str(self.availability.user.username)

    def clean(self):
        # if there are multiple DayAvailability records for the same day of the week, the times should not
        # overlap.
        # find any other records for this `availability` instance which have the same day_of_week
        # if there is any overlap in time, raise ValidationError
        # else we go on our way
        day_a = DayAvailability.objects.filter(availability=self.availability, day_of_week=self.day_of_week)
        if self.pk is None:
            # add the current not-yet-saved instance to the list for bounds checking
            pass
        pass