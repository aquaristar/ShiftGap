from datetime import time, datetime
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
            time_delta = self.end_date - self.start_date
            return time_delta.days
        else:
            return 0

    @property
    def days_rejected(self):
        if self.status == 'R':
            time_delta = self.end_date - self.start_date
            return time_delta.days
        else:
            return 0

    @property
    def days_cancelled(self):
        if self.status == 'C':
            time_delta = self.end_date - self.start_date
            return time_delta.days
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
                start_time=time(0, 0),  # meaning they are not available
                end_time=time(0, 0),
                approved=True
            )
            av.save(approved=True)  # to mark as approved otherwise save method defaults to False on any changes
            self.availability = av
            self.save()

    def reject(self):
        with transaction.atomic():
            self.approved = False
            self.status = 'R'
            self.save()

    def cancel_away(self):
        # reverse the time away operation
        self.status = 'C'
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

    def is_user_available(self, user, date, start_time, end_time):
        # Given a user, date and time, query if the user is available to work or not
        pass

    def user_availability_for_date(self, user, date):
        pass

    def check_shift(self, shift):
        # Given a shift, check to see if conflicts exist
        # Returns True if shift is ok, Returns False if conflict exists
        # first get the relevant

        pass

    def get_availability_for_date(self, user, date):
        # we want to ignore anything that hasn't yet been approved
        av = self.filter(approved=True)
        # see if there is any availability records that correspond for the specific date
        av = av.filter(user=user, start_date__lte=date, end_date__gte=date)

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
    Represents when an employee is available to work.

    start_date
    end_date
        Refers to specific periods of time the availability is in effect for
        If BLANK or Null - then we assume it's 'general' or day to day availability and is in
        effect for all times not represented by an Availability instance with
        start_date and end_date set.
    user
        Who the availability is for

    start_time
    end_time
        The time each day the user is available to work
        If it differs per day then we set these to null and create a DayAvailability record for each
        day of the week in the switch_to_day_availability() method
        When an employee is not available for the date or date range the start_time and end_time
        will both be 00:00:00


    Important - when comparing start_time and end_time, we'll need to join them to the start_date and
    end_date then localize in the users timezone to provide a meaningful response, otherwise we may
    encounter edge cases

    """
    start_date = models.DateField(blank=True, null=True)  # if blank/null we assume this is the users 'general'
    end_date = models.DateField(blank=True, null=True)    # availability aka 'day to day' availability
    user = models.ForeignKey('auth.User')

    # if start time and end time we assume it to be each day for the range start_date to end_date
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    # otherwise we set it on a day of the week basis
    # see DayAvailability model and switch_to_day_availability method

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
        date = self.user.userprofile.timezone.localize(datetime.now())
        return True if date > self.end_date else False

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, approved=False):
        # if modified, we need to get approval again
        if not approved:
            self.approved = False  # unless we're explicitly called approve()

        return super(Availability, self).save()

    def approve(self):
        self.approved = True
        self.save(approved=True)

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

        # Goal: Make sure two Availability instances don't exist with overlapping ranges
        availabilities = Availability.objects.filter(user=self.user)  # put all of your intervals in one array

        av_list = list(availabilities)
        if self.pk is None:  # if it's not saved yet we still need to take the current range into account for validation
            av_list += [self]

        # sort the array by the lower bound of each interval, then the upper bound
        av_list = sorted(av_list, key=lambda x: (x.start_date, x.end_date))

        avs = len(av_list)
        for avx in range(0, avs):
            try:
                overlap = test_overlap(av_list[avx].start_date, av_list[avx].end_date,
                                       av_list[avx+1].start_date, av_list[avx+1].end_date)
                if overlap:
                    raise ValidationError(_('Date ranges cannot overlap'))
            except IndexError:
                pass

        # if there are multiple DayAvailability records for the same day of the week, the times should not
        # overlap.
        for day in self.dayavailability_set.all():
            # NotImplemented yet
            pass

        if self.start_time and self.end_time:
            if self.start_time > self.end_time:
                raise ValidationError(_('Start time is invalid, start time must be before end time.'))

        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(_('Start date is invalid, start date must be before end date.'))

        return super(Availability, self).clean()

    def switch_to_day_availability(self):
        """
        If user needs to define availability on a day of the week basis, this will create the associated
        records required.

        FIXME - This isn't entirely logical. An Availability date range might only be for a day or two
        which doesn't necessitate creating records for each day of the week.
        """
        start_time = self.start_time or time.min  # use current start_time and end_time as default values
        end_time = self.end_date or time.max  # otherwise use min and max
        for day in range(0, 7):

            DayAvailability.objects.create(
                availability=self,
                day_of_week=day,
                start_time=start_time,
                end_time=end_time
            )
        self.start_time = None
        self.end_time = None
        self.save()

    def switch_to_general_availability(self):
        """
        If user wants to define availability in general (e.g. start time to end time for any day) this will
        remove the day of the week records that were created.
        """
        records = self.dayavailability_set.all()
        for record in records:
            record.delete()
        self.start_time = time.min  # some default value
        self.end_time = time.max  # some default value
        self.save()


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