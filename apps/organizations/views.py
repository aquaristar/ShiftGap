from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, Http404
from django.views.generic import View, FormView, UpdateView, CreateView

from braces.views import LoginRequiredMixin

from apps.ui.models import UserProfile
from .models import Organization
from .forms import OrganizationSetupForm


class OrganizationPermission(object):

    def __init__(self, request):
        super().__init__()
        self.request = request

    def has_object_permission(self, obj):
        allow = False
        if hasattr(obj, 'organization_id'):
            up = self._get_user_profile_or_none()
            if up and up.organization_id == obj.organization_id:
                allow = True

        else:
            # Object is not organization owned so permissions do not apply
            allow = True

        return allow

    def filter_object_permissions(self, qs):
        up = self._get_user_profile_or_none()
        if up:
            return qs.filter(organization_id=up.organization_id)
        else:
            return qs.none()

    def _get_user_profile_or_none(self):
        up = None
        if self.request.user.is_authenticated():
            try:
                up = self.request.user.userprofile
            except UserProfile.DoesNotExist:
                pass

        return up


class OrganizationOwnedRequired(LoginRequiredMixin):
    """
    View mixin which verifies that the user owns the object.
    """
    def dispatch(self, request, *args, **kwargs):
        org_perm = OrganizationPermission(request)
        if not org_perm.has_object_permission(self.get_object()):
            raise Http404()

        return super(OrganizationOwnedRequired, self).dispatch(request, *args, **kwargs)


class PostLoginView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            try:
                self.request.user.userprofile
                return HttpResponseRedirect('/')
            except UserProfile.DoesNotExist:
                return HttpResponseRedirect(reverse('account_profile'))
        return HttpResponseRedirect(reverse('login'))


class UserProfileRequiredMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        sup = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated():
            try:
                request.user.userprofile
            except UserProfile.DoesNotExist:
                return HttpResponseRedirect(reverse('account_profile'))

        return sup

# ###### Views


class AccountProfileBaseViewMixin(object):
    template_name = 'organizations/organization_profile.html'
    form_class = OrganizationSetupForm

    def get_success_url(self):
        return reverse('home')


class AccountProfileView(LoginRequiredMixin, AccountProfileBaseViewMixin, CreateView):

    def get(self, request, *args, **kwargs):
        # if the user already has an organization in their user profile, we want them to update the existing record
        try:
            self.request.user.userprofile
            return HttpResponseRedirect(reverse('account_profile_update'))
        except UserProfile.DoesNotExist:
            return super(AccountProfileView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        super(AccountProfileView, self).form_valid(form)
        UserProfile.objects.create(user=self.request.user, organization=self.object, timezone=self.object.default_tz)
        return self.get_success_url()


class AccountProfileUpdateView(LoginRequiredMixin, AccountProfileBaseViewMixin, UpdateView):

    def get_object(self, queryset=None):
        return self.request.user.userprofile.organization