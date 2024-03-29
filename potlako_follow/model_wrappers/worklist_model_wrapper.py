from django.apps import apps as django_apps
from django.conf import settings
from edc_base.utils import get_utcnow
from edc_constants.constants import YES
from edc_model_wrapper import ModelWrapper
from ..models import Call, Log, LogEntry


class LogEntryModelWrapper(ModelWrapper):

    model = 'potlako_follow.logentry'
    querystring_attrs = ['log']
    next_url_attrs = ['log', 'subject_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'potlako_follow_listboard_url')

    @property
    def log(self):
        return self.object.log


class WorkListModelWrapper(ModelWrapper):

    model = 'potlako_follow.worklist'
    querystring_attrs = ['subject_identifier']
    next_url_attrs = ['subject_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'potlako_follow_listboard_url')

    subject_consent_model = 'potlako_subject.subjectconsent'

    @property
    def subject_consent_cls(self):
        return django_apps.get_model(self.subject_consent_model)

    @property
    def specialist_appointment_date(self):
        appt_cls = django_apps.get_model('edc_appointment.appointment')

        appt_obj = appt_cls.objects.filter(
            appt_datetime__lte=get_utcnow().date(),
            appt_status='New',
            subject_identifier=self.object.subject_identifier).latest('-appt_datetime')

        return appt_obj.appt_datetime if appt_obj else None

    @property
    def cancer_propability_suspicion(self):
        baseline_clinical_cls = django_apps.get_model(
            'potlako_subject.baselineclinicalsummary')
        clinician_enrollment_cls = django_apps.get_model(
            'potlako_subject.cliniciancallenrollment')

        try:
            baseline_obj = baseline_clinical_cls.objects.get(
                subject_identifier=self.object.subject_identifier)
        except baseline_clinical_cls.DoesNotExist:
            try:
                clinician_enrollment_obj = clinician_enrollment_cls.objects.get(
                    subject_identifier=self.object.subject_identifier)
            except clinician_enrollment_cls.DoesNotExist:
                return None
            else:
                suspected_cancers = clinician_enrollment_obj.suspected_cancer
                if clinician_enrollment_obj.suspected_cancer_unsure:
                    suspected_cancers += ", " + clinician_enrollment_obj.suspected_cancer_unsure
                if clinician_enrollment_obj.suspected_cancer_other:
                    suspected_cancers += ", " + clinician_enrollment_obj.suspected_cancer_unsure

                return (suspected_cancers, clinician_enrollment_obj.suspicion_level)
        else:
            suspected_cancer = baseline_obj.cancer_concern or baseline_obj.cancer_concern_other
            return (suspected_cancer, baseline_obj.cancer_probability)

    @property
    def subject_locator(self):
        SubjectLocator = django_apps.get_model(
            'potlako_subject.subjectlocator')
        if self.object.subject_identifier:
            try:
                locator = SubjectLocator.objects.get(
                    subject_identifier=self.object.subject_identifier)
            except SubjectLocator.DoesNotExist:
                pass
            else:
                return locator
        return None

    @property
    def call_datetime(self):
        return self.object.called_datetime

    @property
    def call(self):
        call = Call.objects.filter(
            subject_identifier=self.object.subject_identifier).order_by('scheduled').last()
        return str(call.id)

    @property
    def call_log(self):
        call = Call.objects.filter(
            subject_identifier=self.object.subject_identifier).order_by('scheduled').last()
        call_log = Log.objects.get(call=call)
        return str(call_log.id)

    @property
    def log_entries(self):
        wrapped_entries = []
        call = Call.objects.filter(
            subject_identifier=self.object.subject_identifier).order_by('scheduled').last()
        log_entries = LogEntry.objects.filter(
            log__call__subject_identifier=call.subject_identifier).order_by('call_datetime')[:3]
        for log_entry in log_entries:
            wrapped_entries.append(
                LogEntryModelWrapper(log_entry))
        return wrapped_entries

    @property
    def call_attempts(self):
        return len(self.log_entries)

    @property
    def patient_reached(self):
        reached_entries = LogEntry.objects.filter(
            log__call__subject_identifier=self.object.subject_identifier,
            patient_reached=YES)
        return reached_entries[0].patient_reached if reached_entries else None

    @property
    def locator_phone_numbers(self):
        """Return all contact numbers on the locator.
        """
        field_attrs = [
            'subject_cell',
            'subject_cell_alt',
            'subject_phone',
            'subject_phone_alt',
            'subject_work_phone',
            'indirect_contact_cell',
            'indirect_contact_phone']
        if self.subject_locator:
            phone_choices = ()
            for field_attr in field_attrs:
                value = getattr(self.subject_locator, field_attr)
                if value:
                    phone_choices += ((field_attr, value),)
            return phone_choices

    @property
    def call_log_entry_obj(self):
        """Return True if the call log is required.
        """
        try:
            log_obj = LogEntry.objects.get(
                call_datetime__date=get_utcnow().date(),
                log__call__subject_identifier=self.subject_consent.subject_identifier,)
        except LogEntry.DoesNotExist:
            return None
        else:
            return LogEntryModelWrapper(log_obj)

    @property
    def log_entry(self):
        log = Log.objects.get(id=self.call_log)
        logentry = LogEntry(
            log=log,
            subject_identifier=self.object.subject_identifier)
        return LogEntryModelWrapper(logentry)

    @property
    def subject_consent(self):
        return self.subject_consent_cls.objects.filter(
            subject_identifier=self.object.subject_identifier).last()

    @property
    def may_visit_home(self):
        if self.subject_locator:
            return self.subject_locator.may_visit_home
        return None

    @property
    def first_name(self):
        return self.subject_locator.first_name

    @property
    def last_name(self):
        return self.subject_locator.last_name

    @property
    def contacts(self):
        contacts = []
        num_list = ['subject_cell', 'subject_cell_alt',
                    'subject_phone', 'subject_phone_alt']
        for contact in num_list:
            attr = getattr(self.subject_locator, contact, '')
            if attr:
                contacts.append(attr)
            else:
                continue
        return ', '.join(contacts)

    @property
    def survey_schedule(self):
        return None

    @property
    def gender(self):
        return self.subject_consent.gender
