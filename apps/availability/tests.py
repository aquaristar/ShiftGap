import pytz
import datetime

from django.test import TestCase
from django.forms.models import model_to_dict

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
        return av

    def create_approved_availability_with_specific_dates(self):
        """
        Creates an availability record with specific to and from dates and specific from and to times
        :return:
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

    # test clean methods for raiding validation error
    # only one per date range, disallow overlapping
    # test creation of day of the week records DayAvailability
    # test switch back to general availability
    # test approving time off creates availability record
    # test manager gives ok when given shift or error