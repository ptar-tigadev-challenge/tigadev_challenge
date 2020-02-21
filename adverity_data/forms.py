from datetime import date
from django import forms
from bootstrap_datepicker_plus import DatePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Campaign
from .models import Datasource

from .date_util import DATE_FORMAT

class ParametersForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ParametersForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'parameters-form'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'action'

        self.helper.add_input(Submit('submit', 'Load'))

    campaigns = forms.ModelMultipleChoiceField(queryset=Campaign.objects.all())
    datasources = forms.ModelMultipleChoiceField(queryset=Datasource.objects.all())
    date_start = forms.DateField(
            widget = DatePickerInput(format=DATE_FORMAT)
        )
    date_end = forms.DateField(
            widget = DatePickerInput(format=DATE_FORMAT)
        )

