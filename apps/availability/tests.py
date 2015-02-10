import pytz
import datetime

from django.test import TestCase
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from model_mommy import mommy

from apps.ui.models import UserProfile
from apps.organizations.models import Organization
from .models import Availability, TimeOffRequest


class TestAvailabilityLogic(TestCase):

    def setUp(self):
        tz = pytz.timezone('Canada/Mountain')
        self.org = mommy.make(Organization, default_tz=tz)
        up = mommy.make(UserProfile, organization=self.org, timezone=tz)
        self.user = up.user

    def create_approved_availability_general_one(self):
        """
        Creates an availability record for the user as 'general availability'
        e.g. no start or end date is specified
        :return: Availability instance
        """
        av = Availability.objects.create(
            organization=self.org,
            user=self.user,
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(22, 0, 0)
        )
        av.approve()
        av.clean()
        return av

    def create_approved_availability_with_specific_dates(self):
        """
        Creates an availability record with specific to and from dates and specific from and to times
        :return: Availability instance
        """
        av = Availability.objects.create(
            organization=self.org,
            user=self.user,
            start_time=datetime.time(8, 30, 0),  # 8:30 AM
            end_time=datetime.time(23, 30, 0),  # to 11:30 PM
            start_date=datetime.date(2015, 6, 1),  # June 1st
            end_date=datetime.date(2015, 6, 15)  # to June 15th
        )
        av.approve()
        av.clean()
        return av

    def test_can_approve_availability_for_user(self):
        av = self.create_approved_availability_general_one()
        av.approve()
        self.assertTrue(av.approved)

    def test_default_availability_creation_is_not_approved(self):
        av = mommy.make(Availability, user=self.user, organization=self.org)
        self.assertFalse(av.approved)

    def test_availability_has_start_and_end_time_but_no_dates(self):
        av = self.create_approved_availability_general_one()
        self.assertEqual(av.start_time, datetime.time(9, 0, 0))
        self.assertEqual(av.end_time, datetime.time(22, 0, 0))
        self.assertIsNone(av.start_date)
        self.assertIsNone(av.end_date)

    def test_manager_returns_availability_record_for_no_dates(self):
        av = self.create_approved_availability_general_one()
        rec = Availability.objects.get_availability_for_date(user=self.user, date=datetime.datetime.now().date)
        self.assertEqual(model_to_dict(av), model_to_dict(rec))

    def test_manager_returns_availability_record_for_specific_dates(self):
        av = self.create_approved_availability_with_specific_dates()
        rec = Availability.objects.get_availability_for_date(user=self.user, date=datetime.date(2015, 6, 1))
        self.assertEqual(model_to_dict(av), model_to_dict(rec))

    def test_manager_returns_none_if_no_availability_records_exist(self):
        av = Availability.objects.get_availability_for_date(user=self.user, date=datetime.date(2015, 6, 1))
        self.assertIsNone(av)

    def test_start_time_after_end_time_raises_error(self):
        # a start time after the end time should trigger a ValidationError
        av = Availability.objects.create(
            organization=self.org,
            user=self.user,
            start_time=datetime.time(22, 0, 0),
            end_time=datetime.time(9, 0, 0)
        )
        av.approve()
        self.assertRaises(ValidationError, av.clean)

    def test_start_date_after_end_date_raises_error(self):
        # a start date after the end date should trigger a ValidationError
        av = Availability.objects.create(
            organization=self.org,
            user=self.user,
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(22, 0, 0),
            start_date=datetime.date(2015, 6, 15),
            end_date=datetime.date(2015, 6, 1)
        )
        av.approve()
        self.assertRaises(ValidationError, av.clean)

    def test_two_availability_with_null_dates_raises_validation_error(self):
        av = Availability(
            organization=self.org,
            user=self.user,
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(22, 0, 0)
        )
        av.clean()
        av.save()
        self.assertGreater(av.pk, 0)
        av1 = Availability(
            organization=self.org,
            user=self.user,
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(22, 0, 0)
        )
        self.assertRaises(ValidationError, av1.clean)

    def test_two_availability_with_null_dates_raises_validation_error_post_save(self):
        av = Availability(
            organization=self.org,
            user=self.user,
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(22, 0, 0)
        )
        av.clean()
        av.save()
        self.assertGreater(av.pk, 0)
        av1 = Availability(
            organization=self.org,
            user=self.user,
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(22, 0, 0)
        )
        av1.save()
        # why doesn't this cause an IntegrityError because of unique_together = (('start_date', 'end_date', 'user'),)??
        # (None, None, self.user) == (None, None, self.user) == SAME SAME???
        self.assertRaises(ValidationError, av1.clean)

    def test_switch_to_day_of_week_availability(self):
        # we switch from using start_time and end_time to defining start_time and end_time
        # for each day of the week rather than the entire range using DayAvailability records
        av = self.create_approved_availability_general_one()
        av.switch_to_day_availability()
        # one DayAvailability for each day of the week
        self.assertEqual(av.dayavailability_set.all().count(), 7)
        self.assertIsNone(av.start_time)
        self.assertIsNone(av.end_time)

    def test_switch_back_to_general_non_day_of_week_availability(self):
        # we switch from using DayAvailability records to defining start_time and end_time
        # on the Availability instance to define our availability for each day in the range
        av = self.create_approved_availability_general_one()
        av.switch_to_day_availability()
        av.switch_to_general_availability()
        # no DayAvailability records
        self.assertEqual(av.dayavailability_set.all().count(), 0)
        self.assertIsNotNone(av.start_time)
        self.assertIsNotNone(av.end_time)

    # only one per date range, disallow overlapping

    def test_date_range_overlap_raises_validation_error(self):
        av = self.create_approved_availability_with_specific_dates()
        av2 = Availability.objects.create(
            organization=self.org,
            user=self.user,
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(22, 0, 0),
            start_date=datetime.date(2015, 6, 15),
            end_date=datetime.date(2015, 6, 20)
        )
        self.assertRaises(ValidationError, av2.clean)

    def test_another_date_range_overlap_raises_validation_error(self):
        av = self.create_approved_availability_with_specific_dates()
        av2 = Availability.objects.create(
            organization=self.org,
            user=self.user,
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(22, 0, 0),
            start_date=datetime.date(2014, 6, 15),
            end_date=datetime.date(2015, 6, 10)
        )
        self.assertRaises(ValidationError, av2.clean)

    def test_another_date_range_overlap_raises_validation_error_before_save(self):
        av = self.create_approved_availability_with_specific_dates()
        av2 = Availability(
            organization=self.org,
            user=self.user,
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(22, 0, 0),
            start_date=datetime.date(2014, 6, 15),
            end_date=datetime.date(2015, 6, 10)
        )
        self.assertRaises(ValidationError, av2.clean)

    def test_three_date_range_overlap_raises_validation_error_before_save(self):
        av = self.create_approved_availability_with_specific_dates()
        av2 = Availability(
            organization=self.org,
            user=self.user,
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(22, 0, 0),
            start_date=datetime.date(2015, 6, 16),
            end_date=datetime.date(2015, 6, 20)
        )
        av2.clean()
        av2.save()
        av3 = Availability(
            organization=self.org,
            user=self.user,
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(22, 0, 0),
            start_date=datetime.date(2014, 6, 17),
            end_date=datetime.date(2015, 6, 20)
        )
        self.assertRaises(ValidationError, av3.clean)
        self.assertRaises(IntegrityError, av3.save)

    def test_three_date_range_overlap_raises_validation_error(self):
        av = self.create_approved_availability_with_specific_dates()
        av2 = Availability.objects.create(
            organization=self.org,
            user=self.user,
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(22, 0, 0),
            start_date=datetime.date(2015, 6, 16),
            end_date=datetime.date(2015, 6, 20)
        )
        av2.clean()
        # av2.save()
        av3 = Availability.objects.create(
            organization=self.org,
            user=self.user,
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(22, 0, 0),
            start_date=datetime.date(2014, 6, 18),
            end_date=datetime.date(2015, 6, 21)
        )
        self.assertRaises(ValidationError, av3.clean)

    def test_four_date_range_overlap_raises_validation_error(self):
        av = self.create_approved_availability_with_specific_dates()
        av2 = Availability.objects.create(
            organization=self.org,
            user=self.user,
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(22, 0, 0),
            start_date=datetime.date(2015, 6, 15),
            end_date=datetime.date(2015, 6, 20)
        )
        self.assertRaises(ValidationError, av2.clean)
        av3 = Availability.objects.create(
            organization=self.org,
            user=self.user,
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(22, 0, 0),
            start_date=datetime.date(2015, 8, 1),
            end_date=datetime.date(2015, 8, 20)
        )
        av3.clean()  # this raises a ValidationError when it shouldn't
        av4 = Availability(
            organization=self.org,
            user=self.user,
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(22, 0, 0),
            start_date=datetime.date(2015, 7, 1),
            end_date=datetime.date(2015, 8, 1)
        )
        self.assertRaises(ValidationError, av4.clean)

    # test manager gives ok when given shift or error


class TestTimeOffRequestLogic(TestCase):

    def setUp(self):
        tz = pytz.timezone('Canada/Mountain')
        self.org = mommy.make(Organization, default_tz=tz)
        up = mommy.make(UserProfile, organization=self.org, timezone=tz)
        self.user = up.user

    def test_approving_time_off_creates_availability_record(self):
        # approving a users time off should create an associated availability record
        # that reflects the time off
        # self.fail("Not implemented")
        pass

    def test_approving_time_off_is_reflected_in_days_off_property(self):
        pass

    def test_rejecting_time_off_is_reflected_in_days_rejected_property(self):
        pass

    def test_cancelling_time_off_is_reflected_in_days_cancelled_property(self):
        pass