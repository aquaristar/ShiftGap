from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.db.models import QuerySet

from model_mommy import mommy

from apps.ui.models import UserProfile
from .views import AccountProfileView, OrganizationPermission
from .forms import OrganizationSetupForm
from .models import Location, Organization


class TestOrganizationObjectPermissions(TestCase):

    def setUp(self):
        self.org = mommy.make(Organization)
        self.up = mommy.make(UserProfile, organization=self.org)
        self.request = RequestFactory()
        # attach a user to the request for permissions
        self.request.user = self.up.user
        self.permissions_class = OrganizationPermission(request=self.request)

    def test_has_object_permissions(self):
        # we need to use any objects that should belong to an org
        loc2 = mommy.make(Location)
        loc = mommy.make(Location, organization=self.org)
        # loc is owned by self.org
        self.assertTrue(self.permissions_class.has_object_permission(obj=loc))
        # loc2 is owned by some random organization
        self.assertFalse(self.permissions_class.has_object_permission(obj=loc2))

    def test_is_allowed_when_no_organization(self):
        any_non_org_object = TestCase()
        self.assertTrue(self.permissions_class.has_object_permission(obj=any_non_org_object))

    def test_objects_get_filtered(self):
        pass

    def test_returns_none_if_no_user_profile(self):
        pass


class TestOrganizationViews(TestCase):

    def setUp(self):
        self.view = AccountProfileView()

    def test_attrs(self):
        self.assertEqual(self.view.form_class, OrganizationSetupForm)
        self.assertEqual(self.view.get_success_url(), reverse('home'))
        self.assertEqual(self.view.template_name, 'organizations/organization_profile.html')


class LocationHasOrganization(TestCase):

    def test_location_has_organization(self):
        location = mommy.make(Location)
        self.assertTrue(location.organization)