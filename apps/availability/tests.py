import pytz
import datetime

from django.test import TestCase, TransactionTestCase
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from model_mommy import mommy

from apps.ui.models import UserProfile
from apps.organizations.models import Organization, Location
from apps.shifts.models import Shift, Schedule
from .models import Availability, TimeOffRequest, DayAvailability

"""
This code is all written to be run when Canada/Mountain is 7 hours behind UTC.
With DST it's obviously not always 7 hours behind.

Fix it up accordingly.
"""


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
            user=self.user
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
            start_date=datetime.date(2015, 6, 1),  # June 1st
            end_date=datetime.date(2015, 6, 15)  # to June 15th
        )
        av.approve()
        av.clean()
        return av

    def basic_schedule_setup(self):
        """
        Creates a basic schedule (using the org created in setUp)
        :return: Schedule
        """
        loc = mommy.make(Location, organization=self.org)
        sked = mommy.make(Schedule, organization=self.org, location=loc)
        return sked

    def test_can_approve_availability_for_user(self):
        av = self.create_approved_availability_general_one()
        av.approve()
        self.assertTrue(av.approved)

    def test_default_availability_creation_is_not_approved(self):
        av = mommy.make(Availability, user=self.user, organization=self.org)
        self.assertFalse(av.approved)

    def test_availability_has_start_and_end_time_but_no_dates(self):
        av = self.create_approved_availability_general_one()
        self.assertIsNone(av.start_date)
        self.assertIsNone(av.end_date)

    def test_manager_returns_availability_record_for_no_dates(self):
        av = self.create_approved_availability_general_one()
        rec = Availability.objects.get_availability_for_date(user=self.user, av_date=datetime.datetime.now().date)
        self.assertEqual(model_to_dict(av), model_to_dict(rec))

    def test_manager_returns_availability_record_for_specific_dates(self):
        av = self.create_approved_availability_with_specific_dates()
        rec = Availability.objects.get_availability_for_date(user=self.user, av_date=datetime.date(2015, 6, 1))
        self.assertEqual(model_to_dict(av), model_to_dict(rec))

    def test_manager_returns_none_if_no_availability_records_exist(self):
        av = Availability.objects.get_availability_for_date(user=self.user, av_date=datetime.date(2015, 6, 1))
        self.assertIsNone(av)

    def test_start_date_after_end_date_raises_error(self):
        # a start date after the end date should trigger a ValidationError
        av = Availability.objects.create(
            organization=self.org,
            user=self.user,
            start_date=datetime.date(2015, 6, 15),
            end_date=datetime.date(2015, 6, 1)
        )
        av.approve()
        self.assertRaises(ValidationError, av.clean)

    def test_two_availability_with_null_dates_raises_validation_error(self):
        av = Availability(
            organization=self.org,
            user=self.user
        )
        av.clean()
        av.save()
        self.assertGreater(av.pk, 0)
        av1 = Availability(
            organization=self.org,
            user=self.user,
            )
        self.assertRaises(ValidationError, av1.clean)

    def test_two_availability_with_null_dates_raises_validation_error_post_save(self):
        av = Availability(
            organization=self.org,
            user=self.user
        )
        av.clean()
        av.save()
        self.assertGreater(av.pk, 0)
        av1 = Availability(
            organization=self.org,
            user=self.user
        )
        av1.save()
        # why doesn't this cause an IntegrityError because of unique_together = (('start_date', 'end_date', 'user'),)??
        # (None, None, self.user) == (None, None, self.user) == SAME SAME???
        self.assertRaises(ValidationError, av1.clean)

    # only one per date range, disallow overlapping

    def test_date_range_overlap_raises_validation_error(self):
        av = self.create_approved_availability_with_specific_dates()
        av2 = Availability.objects.create(
            organization=self.org,
            user=self.user,
            start_date=datetime.date(2015, 6, 15),
            end_date=datetime.date(2015, 6, 20)
        )
        self.assertRaises(ValidationError, av2.clean)

    def test_another_date_range_overlap_raises_validation_error(self):
        av = self.create_approved_availability_with_specific_dates()
        av2 = Availability.objects.create(
            organization=self.org,
            user=self.user,
            start_date=datetime.date(2014, 6, 15),
            end_date=datetime.date(2015, 6, 10)
        )
        self.assertRaises(ValidationError, av2.clean)

    def test_another_date_range_overlap_raises_validation_error_before_save(self):
        av = self.create_approved_availability_with_specific_dates()
        av2 = Availability(
            organization=self.org,
            user=self.user,
            start_date=datetime.date(2014, 6, 15),
            end_date=datetime.date(2015, 6, 10)
        )
        self.assertRaises(ValidationError, av2.clean)

    def test_three_date_range_overlap_raises_validation_error_before_save(self):
        av = self.create_approved_availability_with_specific_dates()
        av2 = Availability(
            organization=self.org,
            user=self.user,
            start_date=datetime.date(2015, 6, 16),
            end_date=datetime.date(2015, 6, 20)
        )
        av2.clean()
        av2.save()
        av3 = Availability(
            organization=self.org,
            user=self.user,
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
            start_date=datetime.date(2015, 6, 16),
            end_date=datetime.date(2015, 6, 20)
        )
        av2.clean()
        # av2.save()
        av3 = Availability.objects.create(
            organization=self.org,
            user=self.user,
            start_date=datetime.date(2014, 6, 18),
            end_date=datetime.date(2015, 6, 21)
        )
        self.assertRaises(ValidationError, av3.clean)

    def test_four_date_range_overlap_raises_validation_error_plus_general_availability(self):
        av0 = self.create_approved_availability_general_one()
        av = self.create_approved_availability_with_specific_dates()  # 6-1 to 6-15
        av2 = Availability(
            organization=self.org,
            user=self.user,
            start_date=datetime.date(2015, 6, 15),  # offending date range - 'av' above goes to the 15th
            end_date=datetime.date(2015, 6, 20)
        )
        self.assertRaises(ValidationError, av2.clean)
        # av2.save()  # av2 would never get saved because it fails clean() validation
        av3 = Availability.objects.create(
            organization=self.org,
            user=self.user,
            start_date=datetime.date(2015, 8, 1),
            end_date=datetime.date(2015, 8, 20)
        )
        av3.clean()  # this raises a ValidationError when it shouldn't
        av4 = Availability(
            organization=self.org,
            user=self.user,
            start_date=datetime.date(2015, 7, 1),
            end_date=datetime.date(2015, 8, 1)
        )
        self.assertRaises(ValidationError, av4.clean)

    def test_no_day_availability_record_shift_check_true(self):
        """
        Any shift should pass a conflict check at this point since there's no DayAvailability records
        to look up.
        :return:
        """
        av = self.create_approved_availability_general_one()
        sked = self.basic_schedule_setup()
        shift = Shift.objects.create(
            organization=self.org,
            user=self.user,
            schedule=sked,
            start_time=datetime.datetime(2015, 6, 1, 19, 0, 0, tzinfo=pytz.UTC),  # users local time is MST so 12 pm
            end_time=datetime.datetime(2015, 6, 2, 0, 0, 0, tzinfo=pytz.UTC),  # 5 pm local time
            published=True
        )
        check = Availability.objects.check_shift(shift=shift)
        self.assertTrue(check)

    def test_availability_with_specific_dates_shift_check_true_if_no_day_availability(self):
        """
        Availability within a specific date range that has no DayAvailability records should also just
        always return True
        :return:
        """
        av = self.create_approved_availability_with_specific_dates()
        sked = self.basic_schedule_setup()
        shift = Shift.objects.create(
            organization=self.org,
            user=self.user,
            schedule=sked,
            start_time=datetime.datetime(2015, 6, 2, 19, 0, 0, tzinfo=pytz.UTC),  # users local time is MST so 12 pm
            end_time=datetime.datetime(2015, 6, 3, 0, 0, 0, tzinfo=pytz.UTC),  # 5 pm local time
            published=True
        )
        check = Availability.objects.check_shift(shift)
        self.assertTrue(check)

    def test_availability_with_specific_dates_but_no_specific_day_availability_shows_no_conflict(self):
        """
        I feel like my test names will make no sense to an outside developer or even me in 6 months

        Anyway this test has DayAvailability records but none that apply to the shift so it should always
        return True (aka the user is available to work)
        :return:
        """
        av = self.create_approved_availability_with_specific_dates()
        sked = self.basic_schedule_setup()
        av.create_day_availability_record(day_of_week=0)
        shift = Shift.objects.create(
            organization=self.org,
            user=self.user,
            schedule=sked,
            start_time=datetime.datetime(2015, 6, 2, 19, 0, 0, tzinfo=pytz.UTC),  # users local time is MST so 12 pm
            end_time=datetime.datetime(2015, 6, 3, 0, 0, 0, tzinfo=pytz.UTC),  # 5 pm local time
            published=True
        )
        # This shift corresponds to day_of_weel=1 in the users local timezone: Canada/Mountain
        # Therefore no availability record should exist for day_of_week=1, only day_of_week=0
        # Meaning the user should show as available, e.g. check_shift(shift) should return True
        check = Availability.objects.check_shift(shift)
        self.assertTrue(check)

    def test_multiple_availability_windows_for_same_day_of_week(self):
        """
        If we have more than one DayAvailability record for a specific day of the week and are searching for
        the users availability, it should respect BOTH ranges specified.

        Availability:
        9 AM to 12 PM
        3 PM to 6 PM

        Shifts (validate):
        These are all based on June 2015, DST is in effect so observing MDT (not MST) so 6 hours behind UTC not the normal 7
        8 AM to 12 PM (fails validation as the user isn't available until 9 AM)
        9 AM to 11 AM (passes because it's within the 9 AM to 12 PM window)
        4 PM to 5 PM (passes because it's within the 3pm to 6pm window)
        5 PM to 8 PM (fails because it's beyond the latest 6 PM window)
        9 AM to 12 PM (passes because it's exactly within the 9 AM to 12 PM window)
        9 AM to 11:59:59 AM (just for fun it clearly passes)

        :return:
        """
        sked = self.basic_schedule_setup()
        av = self.create_approved_availability_with_specific_dates()  # June 1st to June 15th, 2015
        for day in range(0, 7):
            # Creates an availability record for each day from 9 AM to 12 PM and 3 PM to 6 PM
            av.create_day_availability_record(day_of_week=day, av_start_time=datetime.time(9, 0, 0),
                                              av_end_time=datetime.time(12, 0, 0))
            av.create_day_availability_record(day_of_week=day, av_start_time=datetime.time(15, 0, 0),
                                              av_end_time=datetime.time(18, 0, 0))

        # ############ Shift 1 from 8 AM to 12 PM should fail validation
        s1 = Shift(
            organization=self.org,
            user=self.user,
            schedule=sked,
            start_time=datetime.datetime(2015, 6, 2, 14, 0, 0, tzinfo=pytz.UTC),  # users local time is MST so 8 AM
            end_time=datetime.datetime(2015, 6, 2, 18, 0, 0, tzinfo=pytz.UTC),  # 12 pm local time
            published=True
        )
        check1 = Availability.objects.check_shift(s1)
        self.assertFalse(check1)  # 8 AM is too early so check should fail/be False

        # ############ Shift 2 from 9 AM to 11 AM should pass validation
        s2 = Shift(
            organization=self.org,
            user=self.user,
            schedule=sked,
            start_time=datetime.datetime(2015, 6, 2, 15, 0, 0, tzinfo=pytz.UTC),
            end_time=datetime.datetime(2015, 6, 2, 17, 0, 0, tzinfo=pytz.UTC),
            published=True
        )
        check2 = Availability.objects.check_shift(s2)
        self.assertTrue(check2)  # is within bounds of 9 AM to 12 PM so should pass/be True

        # ############ Shift 3 from 4 PM to 5 PM should pass validation
        s3 = Shift(
            organization=self.org,
            user=self.user,
            schedule=sked,
            start_time=datetime.datetime(2015, 6, 2, 22, 0, 0, tzinfo=pytz.UTC),
            end_time=datetime.datetime(2015, 6, 2, 23, 0, 0, tzinfo=pytz.UTC),
            published=True
        )
        check3 = Availability.objects.check_shift(s3)
        self.assertTrue(check3)  # is within bounds of 3 PM to 6 PM so should pass/be True

        # ############ Shift 4 from 5 PM to 8 PM should fail validation
        s4 = Shift(
            organization=self.org,
            user=self.user,
            schedule=sked,
            start_time=datetime.datetime(2015, 6, 2, 23, 0, 0, tzinfo=pytz.UTC),
            end_time=datetime.datetime(2015, 6, 3, 2, 0, 0, tzinfo=pytz.UTC),  # 02:00 next day but 8 PM loc time
            published=True
        )
        check4 = Availability.objects.check_shift(s4)
        self.assertFalse(check4)  # is past bounds of 3 PM to 6 PM so should fail/be False

        # ############ Shift 5 from 9 AM to 12 PM should pass validation
        s5 = Shift(
            organization=self.org,
            user=self.user,
            schedule=sked,
            start_time=datetime.datetime(2015, 6, 2, 15, 0, 0, tzinfo=pytz.UTC),
            end_time=datetime.datetime(2015, 6, 2, 18, 0, 0, tzinfo=pytz.UTC),
            published=True
        )
        check5 = Availability.objects.check_shift(s5)
        self.assertTrue(check5)  # is exactly within bounds of 9 AM to 12 PM so should pass/be True

        # ############ Shift 5 from 9 AM to 11:59:59 AM should pass validation
        s6 = Shift(
            organization=self.org,
            user=self.user,
            schedule=sked,
            start_time=datetime.datetime(2015, 6, 2, 15, 0, 0, tzinfo=pytz.UTC),
            end_time=datetime.datetime(2015, 6, 2, 17, 59, 59, tzinfo=pytz.UTC),
            published=True
        )
        check6 = Availability.objects.check_shift(s6)
        self.assertTrue(check6)  # is within bounds of 9 AM to 12 PM so should pass/be True

    def test_multi_day_shift_validations_uses_multiple_availability_records(self):
        """
        A shift that spans multiple days can have multiple availability records (one corresponding to
        each day).

        Most common situation is for businesses that are open late
            e.g. shift from 8 PM to 2 AM

        Although unrealistic let's also sets a shift that spans several days...
            e.g. shift from 8 PM to (+2 days later) 8 PM

        :return:
        """
        sked = self.basic_schedule_setup()
        av = self.create_approved_availability_with_specific_dates()  # June 1st to June 15th, 2015
        for day in range(0, 7):
            # Creates an availability record for each day from 9 AM to 12 PM and 3 PM to 6 PM
            av.create_day_availability_record(day_of_week=day, av_start_time=datetime.time(9, 0, 0),
                                              av_end_time=datetime.time(12, 0, 0))
            av.create_day_availability_record(day_of_week=day, av_start_time=datetime.time(15, 0, 0),
                                              av_end_time=datetime.time(18, 0, 0))

        av2 = Availability.objects.create(
            organization=self.org,
            user=self.user,
            start_date=datetime.date(2015, 5, 1),  # June 1st
            end_date=datetime.date(2015, 5, 31)  # to June 15th
        )
        av2.approve()
        av2.clean()
        for day in range(0, 7):
            av2.create_day_availability_record(day_of_week=day, av_start_time=datetime.time(8, 0, 0),
                                               av_end_time=datetime.time(23, 0, 0))

        # ############ Shift 5 from 9 AM to 12 pm from may 30 to june 5 should fail validation
        s6 = Shift(
            organization=self.org,
            user=self.user,
            schedule=sked,
            start_time=datetime.datetime(2015, 5, 30, 13, 0, 0, tzinfo=pytz.UTC),  # (2015, 5, 30, 15, 0, 0,
            end_time=datetime.datetime(2015, 6, 2, 18, 0, 0, tzinfo=pytz.UTC),
            published=True
        )
        check6 = Availability.objects.check_shift(s6)
        self.assertFalse(check6)  # is within bounds of 9 AM to 12 PM so should pass/be True
        """
        This is a failing test case that needs to be fixed. See models.py:165 FIXME.
        """

    def test_day_availability_record_creation_does_not_allow_overlap(self):
        """
        Multiple day availability records for the same day should not allow time overlap.

        e.g. You should not be able to create availability records for 9AM to 12 PM and 10AM - 1 PM because they overlap.
        :return:
        """
        sked = self.basic_schedule_setup()
        av = self.create_approved_availability_with_specific_dates()  # June 1st to June 15th, 2015

        da = DayAvailability(
            availability=av,
            day_of_week=0,
            start_time=datetime.time(9, 0, 0),
            end_time=datetime.time(17, 0, 0)
        )
        da.clean()
        da.save()

        da2 = DayAvailability(
            availability=av,
            day_of_week=0,
            start_time=datetime.time(16, 0, 0),
            end_time=datetime.time(17, 0, 0)
        )
        self.assertRaises(ValidationError, da2.clean)  # this overlaps with 9 AM to 5 PM we just saved above

        da3 = DayAvailability(
            availability=av,
            day_of_week=0,
            start_time=datetime.time(17, 0, 0),
            end_time=datetime.time(18, 0, 0)
        )
        da3.clean()
        da3.save()

    def test_day_availability_record_creation_does_not_start_time_before_end_time(self):
        """
        DayAvailability records where time ranges don't make sense should raise ValidationError
        10 AM to 9 AM -> should fail

        :return:
        """
        sked = self.basic_schedule_setup()
        av = self.create_approved_availability_with_specific_dates()  # June 1st to June 15th, 2015
        # for day in range(0, 7):
        # Creates an availability record for each day 10 AM to 9 AM which should be invalid
        da = DayAvailability(
            availability=av,
            day_of_week=0,
            start_time=datetime.time(10, 0, 0),
            end_time=datetime.time(9, 0, 0)
        )
        self.assertRaises(ValidationError, da.clean)
        da2 = DayAvailability(
            availability=av,
            day_of_week=0,
            start_time=datetime.time(10, 0, 0),
            end_time=datetime.time(10, 0, 0)
        )
        da2.clean()

    def test_expired_availability_shows_expired(self):
        """
        Availability records in the past should reflect that they are 'expired'
        :return:
        """
        av = Availability.objects.create(
            organization=self.org,
            user=self.user,
            start_date=datetime.date(2014, 6, 1),  # June 1st
            end_date=datetime.date(2014, 6, 15)  # to June 15th
        )
        av.approve()
        av.clean()
        self.assertTrue(av.expired)

    def test_non_expired_availability_shows_not_expired(self):
        """
        Availability records in the future should reflect that they are NOT 'expired'
        :return:
        """
        av = Availability.objects.create(
            organization=self.org,
            user=self.user,
            start_date=datetime.date(2018, 6, 1),  # June 1st
            end_date=datetime.date(2018, 6, 15)  # to June 15th
        )
        av.approve()
        av.clean()
        self.assertFalse(av.expired)

    def test_resetting_daily_availability_clears_day_availability_records(self):
        """
        Calling reset_daily_availability() on any Availability instance should remove any associated
        DayAvailability records
        :return:
        """
        av = self.create_approved_availability_with_specific_dates()  # June 1st to June 15th, 2015
        for day in range(0, 7):
            DayAvailability.objects.create(
                availability=av,
                day_of_week=0,
                start_time=datetime.time(10, 0, 0),
                end_time=datetime.time(11, 0, 0)
            )
        # FIXME is this even a valid test? do we need to 're-get' the av instance from the database for
        # actual confirmation and use TransactionTestCase for this test class?
        av.reset_daily_availability()
        self.assertCountEqual(av.dayavailability_set.all(), [])


class TestTimeOffRequestLogic(TransactionTestCase):

    def setUp(self):
        tz = pytz.timezone('Canada/Mountain')
        self.org = mommy.make(Organization, default_tz=tz)
        up = mommy.make(UserProfile, organization=self.org, timezone=tz)
        self.user = up.user

    def create_time_off_request(self):
        request = TimeOffRequest(
            organization=self.org,
            start_date=datetime.date(2015, 8, 1),
            end_date=datetime.date(2015, 9, 2),
            user=self.user,
            request_note='Pretty please...'
        )
        request.clean()
        request.save()
        return request

    def create_time_off_request_for_two_days(self):
        request = TimeOffRequest(
            organization=self.org,
            start_date=datetime.date(2015, 10, 1),
            end_date=datetime.date(2015, 10, 2),
            user=self.user,
            request_note='Pretty please...'
        )
        request.clean()
        request.save()
        return request

    def basic_schedule_setup(self):
        """
        Creates a basic schedule (using the org created in setUp)
        :return: Schedule
        """
        loc = mommy.make(Location, organization=self.org)
        sked = mommy.make(Schedule, organization=self.org, location=loc)
        return sked

    def test_approving_time_off_creates_availability_record(self):
        # approving a users time off should create an associated availability record
        # that reflects the time off
        # self.fail("Not implemented")
        req = self.create_time_off_request()  # August 1st to September 2nd
        req.approve()
        av = Availability.objects.get_availability_for_date(user=self.user, av_date=datetime.date(2015, 8, 2))
        self.assertIsNotNone(av)  # FIXME this should probably check a lot more

    def test_shift_raises_conflict_if_during_users_approved_time_off(self):
        req = self.create_time_off_request()  # August 1st to September 2nd, 2015
        req.approve()
        sked = self.basic_schedule_setup()

        # This is the user being scheduled during their approved vacation
        s1 = Shift(
            organization=self.org,
            user=self.user,
            schedule=sked,
            start_time=datetime.datetime(2015, 8, 15, 14, 0, 0, tzinfo=pytz.UTC),  # users local time is MST so 8 AM
            end_time=datetime.datetime(2015, 8, 15, 18, 0, 0, tzinfo=pytz.UTC),  # 12 pm local time
            published=True
        )
        s1.save()
        check = Availability.objects.check_shift(s1)
        self.assertFalse(check)  # during users vacation so shows conflict

        # This is the user being scheduled right after their vacation ends
        s2 = Shift(
            organization=self.org,
            user=self.user,
            schedule=sked,
            start_time=datetime.datetime(2015, 9, 3, 14, 0, 0, tzinfo=pytz.UTC),  # users local time is MST so 8 AM
            end_time=datetime.datetime(2015, 9, 3, 18, 0, 0, tzinfo=pytz.UTC),  # 12 pm local time
            published=True
        )
        s2.save()
        check2 = Availability.objects.check_shift(s2)
        self.assertTrue(check2)  # after users vacation so the shift shows no conflict

    def test_approving_time_off_is_reflected_in_days_approved_property(self):
        req = self.create_time_off_request_for_two_days()
        req.approve()
        self.assertEqual(req.days_approved, 2)
        self.assertEqual(req.days_rejected, 0)
        self.assertEqual(req.days_cancelled, 0)

    def test_rejecting_time_off_is_reflected_in_days_rejected_property(self):
        req = self.create_time_off_request_for_two_days()
        req.reject()
        self.assertEqual(req.days_rejected, 2)
        self.assertEqual(req.days_approved, 0)
        self.assertEqual(req.days_cancelled, 0)

    def test_cancelling_time_off_is_reflected_in_days_cancelled_property(self):
        req = self.create_time_off_request_for_two_days()
        req.cancel_away()
        self.assertEqual(req.days_rejected, 0)
        self.assertEqual(req.days_approved, 0)
        self.assertEqual(req.days_cancelled, 2)

    def test_end_date_before_start_date_raises_validation_error(self):
        request = TimeOffRequest(
            organization=self.org,
            start_date=datetime.date(2015, 10, 1),
            end_date=datetime.date(2014, 10, 2),
            user=self.user,
            request_note='Pretty please...'
        )
        self.assertRaises(ValidationError, request.clean)

    def test_cancelling_away_removes_availability_record(self):
        # cancelling away should remove the availability record
        req = self.create_time_off_request()  # August 1st to September 1st
        req.approve()
        av = Availability.objects.get_availability_for_date(user=self.user, av_date=datetime.date(2015, 8, 2))
        availability_id = req.availability_id  # original availability pk that was created
        req.cancel_away()
        req = TimeOffRequest.objects.get(pk=req.pk)
        self.assertIsNone(req.availability)
        self.assertRaises(Availability.DoesNotExist, Availability.objects.get, pk=availability_id)
