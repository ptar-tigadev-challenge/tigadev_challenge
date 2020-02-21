from datetime import date
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Campaign
from .models import Datasource

from .date_util import DATE_FORMAT

class ParametersForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ParametersForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = ''

        self.helper.add_input(Submit('submit', 'Load'))

    campaigns = forms.ModelMultipleChoiceField(queryset=Campaign.objects.all())
    datasources = forms.ModelMultipleChoiceField(queryset=Datasource.objects.all())
    start_date = forms.DateField(
            widget=forms.DateInput(attrs={'type':'date'})
        )
    end_date = forms.DateField(
            widget=forms.DateInput(attrs={'type':'date'}),
        )

