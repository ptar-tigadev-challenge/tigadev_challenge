from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Campaign
from .models import Datasource

BIRTH_YEAR_CHOICES = ['1980', '1981', '1982']
FAVORITE_COLORS_CHOICES = [
    ('blue', 'Blue'),
    ('green', 'Green'),
    ('black', 'Black'),
]

class ParametersForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ParametersForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'

        self.helper.add_input(Submit('submit', 'Load'))

    campaigns = forms.ModelMultipleChoiceField(queryset=Campaign.objects.all())
    datasources = forms.ModelMultipleChoiceField(queryset=Datasource.objects.all())
    start_date = forms.DateField(
            widget=forms.TextInput(
                attrs={'type': 'date'}
            )
        )
    end_date = forms.DateField(
            widget=forms.TextInput(
                attrs={'type': 'date'}
            )
        )

