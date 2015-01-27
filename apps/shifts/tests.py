from django.test import TestCase
from django.core.urlresolvers import reverse

from .views import ShiftListView, ShiftListCalendarView
from .forms import ShiftForm


class TestShiftListViews(TestCase):

    def setUp(self):
        self.view = ShiftListView()

    def test_attrs(self):
        # self.assertEqual(self.view.form_class, OrganizationSetupForm)
        self.assertEqual(self.view.get_success_url(), reverse('shifts:shift_list'))
        self.assertEqual(self.view.from_, None)
        self.assertEqual(self.view.to, None)
        self.assertEqual(self.view.template_name, 'shifts/shift_list.html')
        self.assertEqual(self.view.form_class, ShiftForm)


class TestShiftCalendarView(TestCase):

    def setUp(self):
        self.view = ShiftListCalendarView()

    def test_attrs(self):
        self.assertEqual(self.view.template_name, 'shifts/shift_calendar.html')

    def test_context_data(self):
        pass