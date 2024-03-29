from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, Http404
from django.views.generic import View, UpdateView, CreateView, ListView, TemplateView
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import ugettext as _

from braces.views import LoginRequiredMixin

from apps.ui.models import UserProfile
from apps.shifts.models import Schedule
from apps.phone.tasks import send_user_phone_confirmation_code
from .models import Organization, Location
from .forms import OrganizationSetupForm, UserSetupForm, UserSetupWithoutOrganizationForm, UserEditForm


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
        if request.user.is_authenticated():
            try:
                UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                return HttpResponseRedirect(reverse('account_profile'))
        return super().dispatch(request, *args, **kwargs)

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
            UserProfile.objects.get(user=request.user)
            return HttpResponseRedirect(reverse('account_profile_update'))
        except UserProfile.DoesNotExist:
            return super(AccountProfileView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        super(AccountProfileView, self).form_valid(form)
        UserProfile.objects.create(user=self.request.user, organization=self.object, timezone=self.object.default_tz,
                                   role='ADM')
        # FIXME move this to another user initiated view
        default_location = Location.objects.create(name='Default', organization=self.object, timezone=self.object.default_tz)
        Schedule.objects.create(name='Default', organization=self.object, location=default_location)
        return HttpResponseRedirect(self.get_success_url())


class AccountProfileUpdateView(LoginRequiredMixin, AccountProfileBaseViewMixin, UpdateView):
    template_name = 'organizations/organization_profile_update.html'

    def get_object(self, queryset=None):
        return self.request.user.userprofile.organization

    def form_valid(self, form):
        super(AccountProfileUpdateView, self).form_valid(form)
        self.request.user.userprofile.timezone = self.object.default_tz
        return HttpResponseRedirect(self.get_success_url())


class UserListView(UserProfileRequiredMixin, ListView):
    model = User
    template_name = 'organizations/user_list.html'

    def get_queryset(self):
        return User.objects.filter(userprofile__organization=self.request.user.userprofile.organization, userprofile__active=True)

    def post(self, request, *args, **kwargs):
        if self.request.user.userprofile.phone_number:
            user_id = request.POST['user_id']
            send_user_phone_confirmation_code.delay(user_id)
            messages.success(request, _('You should be receiving a confirmation text shortly!'))
            return HttpResponseRedirect(reverse('phone:confirm_phone'))
        else:
            messages.error(request, _("You need to have a phone number saved to your profile before you can confirm it,"))
            return HttpResponseRedirect(reverse('org:user_list'))


class NonActiveUserListView(UserProfileRequiredMixin, ListView):
    model = User
    template_name = 'organizations/user_list_non_active.html'

    def get_queryset(self):
        return User.objects.filter(userprofile__organization=self.request.user.userprofile.organization, userprofile__active=False)

    def post(self, request, *args, **kwargs):
        if self.request.user.userprofile.phone_number:
            user_id = request.POST['user_id']
            send_user_phone_confirmation_code.delay(user_id)
            messages.success(request, _('You should be receiving a confirmation text shortly!'))
            return HttpResponseRedirect(reverse('phone:confirm_phone'))
        else:
            messages.error(request, _("You need to have a phone number saved to your profile before you can confirm it,"))
            return HttpResponseRedirect(reverse('org:user_list'))


# FIXME: Better permissions implementation this is a quick and dirty fix
class ManagerOrAdminRoleRequiredMixin(UserProfileRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        # make sure there is a UserProfile before we go any further
        sup = super().dispatch(request, *args, **kwargs)
        if self.request.user.userprofile.role != 'MGR' and self.request.user.userprofile.role != 'ADM':
            messages.warning(self.request, _("Manager or admin privileges are required to complete this operation."))
            return HttpResponseRedirect('/')
        else:
            return sup


class DeactivateUserView(ManagerOrAdminRoleRequiredMixin, TemplateView):
    template_name = 'organizations/deactivate_user.html'

    def get_context_data(self, **kwargs):
        context = super(DeactivateUserView, self).get_context_data(**kwargs)
        context['deactivate_user'] = User.objects.get(pk=self.kwargs['pk'], userprofile__organization=self.request.user.userprofile.organization)
        return context

    def post(self, *args, **kwargs):
        userp = UserProfile.objects.get(user__pk=self.kwargs['pk'], organization=self.request.user.userprofile.organization)
        userp.deactivate_user()
        messages.success(self.request, _('User %s has been successfully deactivated.') % userp.user.first_name)
        return HttpResponseRedirect(reverse('org:user_list'))


class ReactivateUserView(ManagerOrAdminRoleRequiredMixin, TemplateView):
    template_name = 'organizations/reactivate_user.html'

    def get_context_data(self, **kwargs):
        context = super(ReactivateUserView, self).get_context_data(**kwargs)
        context['reactivate_user'] = User.objects.get(pk=self.kwargs['pk'], userprofile__organization=self.request.user.userprofile.organization)
        return context

    def post(self, *args, **kwargs):
        userp = UserProfile.objects.get(user__pk=self.kwargs['pk'], organization=self.request.user.userprofile.organization)
        userp.reactivate_user()
        messages.success(self.request, _('User %s has been successfully reactivated.') % userp.user.first_name)
        return HttpResponseRedirect(reverse('org:user_list'))


class UserEditView(UserProfileRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserEditForm
    template_name = 'organizations/userprofile_form.html'

    def get_initial(self):
        initial = {'first_name': self.get_object().user.first_name,
                   'last_name': self.get_object().user.last_name}
        return initial

    def form_valid(self, form):
        user = self.get_object().user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        if form.cleaned_data['password']:
            user.set_password(form.cleaned_data['password'])
        user.save()
        return super(UserEditView, self).form_valid(form=form)

    def get_success_url(self):
        return reverse('org:user_list')

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        if self.request.user.userprofile.pk != int(pk) and not self.request.user.userprofile.admin_or_manager:
            messages.warning(request, _("You can only modify your own profile. To modify another users profile,"
                                      "you must be an admin or manager."))
            return HttpResponseRedirect(reverse('org:user_list'))
        # make sure we are editing a user of the same organization
        if UserProfile.objects.get(pk=pk).organization != self.request.user.userprofile.organization:
            messages.warning(request, _("You can't modify a user profile from another organization."))
            return HttpResponseRedirect(reverse('org:user_list'))
        else:
            return super(UserEditView, self).dispatch(request, *args, **kwargs)


class UserProfileCreateMixin(object):
    model = UserProfile
    form_class = UserSetupForm
    template_name = 'organizations/userprofile_form.html'

    def get_form_kwargs(self):
        kwargs = super(UserProfileCreateMixin, self).get_form_kwargs()
        kwargs = kwargs.copy()
        kwargs['request'] = self.request
        return kwargs


class UserSetupView(ManagerOrAdminRoleRequiredMixin, UserProfileCreateMixin, CreateView):

    def get_success_url(self):
        return reverse('org:user_list')


class JoinExistingOrganizationView(LoginRequiredMixin, UserProfileCreateMixin, CreateView):
    form_class = UserSetupWithoutOrganizationForm

    def get_success_url(self):
        return reverse('shifts:shift_calendar')