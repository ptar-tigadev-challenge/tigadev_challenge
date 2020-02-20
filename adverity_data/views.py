from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from .models import Campaign
from .models import Datasource
from .forms import ParametersForm

class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ParametersForm()
        return context

class AdverityDataJSONView(BaseLineChartView):

    def get_labels(self):
        """Return 7 labels for the x-axis."""
        return ["January", "February", "March", "April", "May", "June", "July"]

    def get_providers(self):
        """Return names of datasets."""
        return ["Central", "Eastside", "Westside"]

    def get_data(self):
        """Return 3 datasets to plot."""

        return [[75, 44, 92, 11, 44, 95, 35],
                [41, 92, 18, 3, 73, 87, 92],
                [87, 21, 94, 3, 90, 13, 65]]

index_view = IndexView.as_view()
adverity_data_json = AdverityDataJSONView.as_view()
