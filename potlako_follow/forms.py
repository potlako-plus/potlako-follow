from django import forms
from django.apps import apps as django_apps
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

from edc_base.sites import SiteModelFormMixin
from edc_constants.constants import YES, CLOSED, NO
from edc_form_validators import FormValidator
from edc_form_validators import FormValidatorMixin

from .models import LogEntry, NavigationWorkList, WorkList, InvestigationFUWorkList


class LogEntryFormValidator(FormValidator):

    def clean(self):
        cleaned_data = self.cleaned_data
        log = cleaned_data.get('log')

        if cleaned_data.get('patient_reached') == YES and not cleaned_data.get('call_outcome'):
            message = {
                'call_outcome':
                'This field is required'}
            self._errors.update(message)
            raise ValidationError(message)
        elif cleaned_data.get('patient_reached') == NO and cleaned_data.get('call_outcome'):
            message = {
                'call_outcome':
                'This field is not required'}
            self._errors.update(message)
            raise ValidationError(message)
        

        self.required_if(NO,
                         field='patient_reached', field_required='comment', inverse=False)

        if log.call.call_status == CLOSED:
            message = {
                '__all__':
                'This call is closed. You may not add to or change the call log.'}
            self._errors.update(message)
            raise ValidationError(message)
        


class LogEntryForm(FormValidatorMixin, forms.ModelForm):

    form_validator_cls = LogEntryFormValidator

    subject_identifier = forms.CharField(
        label='Subject Identifier',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        required=False)

    class Meta:
        model = LogEntry
        fields = '__all__'


class WorkListForm(SiteModelFormMixin, forms.ModelForm):

    class Meta:
        model = WorkList
        fields = '__all__'


class NavigationWorkListForm(SiteModelFormMixin, forms.ModelForm):

    class Meta:
        model = NavigationWorkList
        fields = '__all__'


class InvestigationFUWorkListForm(SiteModelFormMixin, forms.ModelForm):

    class Meta:
        model = InvestigationFUWorkList
        fields = '__all__'


class AssignParticipantForm(forms.Form):

    username = forms.ChoiceField(
        required=True, label='Username',
        widget=forms.Select())

    participants = forms.IntegerField(
        required=True, label='Total participants')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].choices = self.assign_users
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'assign_participant'
        self.helper.form_action = 'flourish_follow:home_url'

        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'username',
            'participants',  # field1 will appear first in HTML
            Submit('submit', u'Assign', css_class="btn btn-sm btn-default"),
        )

    @property
    def assign_users(self):
        """Reurn a list of users that can be assigned an issue.
        """
        assignable_users_choices = ()
        user = django_apps.get_model('auth.user')
        app_config = django_apps.get_app_config('potlako_follow')
        assignable_users_group = app_config.assignable_users_group
        try:
            Group.objects.get(name=assignable_users_group)
        except Group.DoesNotExist:
            Group.objects.create(name=assignable_users_group)
        assignable_users = user.objects.filter(
            groups__name=assignable_users_group)
        extra_choices = ()
        if app_config.extra_assignee_choices:
            for _, value in app_config.extra_assignee_choices.items():
                extra_choices += (value[0],)
        for assignable_user in assignable_users:
            username = assignable_user.username
            if not assignable_user.first_name:
                raise ValidationError(
                    f"The user {username} needs to set their first name.")
            if not assignable_user.last_name:
                raise ValidationError(
                    f"The user {username} needs to set their last name.")
            full_name = (f'{assignable_user.first_name} '
                         f'{assignable_user.last_name}')
            assignable_users_choices += ((username, full_name),)
        if extra_choices:
            assignable_users_choices += extra_choices
        return assignable_users_choices


class ResetAssignmentForm(forms.Form):

    username = forms.ChoiceField(
        required=True, label='Username',
        widget=forms.Select())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].choices = self.assign_users
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'assign_participant'
        self.helper.form_action = 'flourish_follow:home_url'

        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'username',
            Submit('submit', u'Reset', css_class="btn btn-sm btn-default"),
        )

    @property
    def assign_users(self):
        """Reurn a list of users that can be assigned an issue.
        """
        assignable_users_choices = (('all', 'All'),)
        user = django_apps.get_model('auth.user')
        app_config = django_apps.get_app_config('potlako_follow')
        assignable_users_group = app_config.assignable_users_group
        try:
            Group.objects.get(name=assignable_users_group)
        except Group.DoesNotExist:
            Group.objects.create(name=assignable_users_group)
        assignable_users = user.objects.filter(
            groups__name=assignable_users_group)
        extra_choices = ()
        if app_config.extra_assignee_choices:
            for _, value in app_config.extra_assignee_choices.items():
                extra_choices += (value[0],)
        for assignable_user in assignable_users:
            username = assignable_user.username
            if not assignable_user.first_name:
                raise ValidationError(
                    f"The user {username} needs to set their first name.")
            if not assignable_user.last_name:
                raise ValidationError(
                    f"The user {username} needs to set their last name.")
            full_name = (f'{assignable_user.first_name} '
                         f'{assignable_user.last_name}')
            assignable_users_choices += ((username, full_name),)
        if extra_choices:
            assignable_users_choices += extra_choices
        return assignable_users_choices


class ParticipantsNumberForm(forms.Form):

    participants = forms.IntegerField(
        required=True, label='Request participants')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'select_participant'
        self.helper.form_action = 'flourish_follow:flourish_follow_listboard_url'

        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'participants',  # field1 will appear first in HTML
            Submit('submit', u'Randomize', css_class="btn btn-sm btn-default"),
        )
