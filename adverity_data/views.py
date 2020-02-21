from datetime import datetime
from datetime import timedelta

from django.views.generic import TemplateView
from django.db.models import Q

from chartjs.views.lines import BaseLineChartView
from .models import Datasource
from .models import Campaign
from .models import Click
from .models import Impression

from .apps import AdverityDataConfig

from .forms import ParametersForm

from .date_util import DATE_FORMAT
from .date_util import get_date_from_model


class IndexView(TemplateView):
    """Class to render main page conaining parameters form and chart"""

    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = ParametersForm()
        dates = get_date_from_model(None, None)
        form.fields['date_start'].initial = dates[0].date
        form.fields['date_end'].initial = dates[1].date
        context['form'] = form
        return context


class AdverityDataJSONView(BaseLineChartView):
    """Class to render JSON with data required to draw chart"""

    def __init__(self):

        self._date_start, self._date_end = get_date_from_model(
                   None,
                   None
            )
        """Filter by dates"""

        self._datasources = None
        """Filter by datasource"""

        self._campaigns = Campaign.objects.filter(
              name__in=AdverityDataConfig.default_campaigns
              )
        """Filter by campaigns"""

        self._date_range = {}
        """Date sequence without gaps, used to create chart labels"""

        self._datasets = {}
        """Datasets, used to create chartjs list datasets.
        Each key - tuple of datasource:campaing"""

        self._loaded_datasources = {}
        """Cache for datasource objects, retrieved while data selected.
        Used to create human readable names for charts"""

        self._loaded_campaigns = {}
        """Cache for campaing objects, retrieved while data selected.
        Used to create human readable names for charts"""

    def post(self, request, *args, **kwargs):
        return self.get(request, args, kwargs)

    def get_context_data(self, **kwargs):
        context = super(BaseLineChartView, self).get_context_data(**kwargs)
        if self.request.method == 'POST':
            form = ParametersForm(self.request.POST)
            if form.is_valid():
                self._date_start = form.cleaned_data['date_start']
                self._date_end = form.cleaned_data['date_end']
                self._datasources = form.cleaned_data['datasources']
                self._campaigns = form.cleaned_data['campaigns']
            else:
                print(form.errors)

        self.generate_date_range(self._date_start, self._date_end)
        self.prepare_datasets()
        context.update(
            {
              "labels": self.get_labels(),
              'datasets': self.get_datasets()
            }
          )
        return context

    def generate_date_range(self, date_start, date_end):
        """Generate sequence of dates starting
        from date_start up to date_end (inclusive).
        For each key index stored, to allow properly place retrieved data"""
        new_date = date_start
        index = 0
        while new_date <= date_end:
            self._date_range[datetime.strftime(new_date, DATE_FORMAT)] = index
            index = index + 1
            new_date = new_date + timedelta(days=1)
        self._labels = list(self._date_range.keys())

    def cache_fk_data(self, cls, pk):
        """Utility function to store information
        about Campaign or Datasource"""
        if cls == Datasource:
            self._loaded_datasources.setdefault(
                pk,
                cls.objects.get(id=pk)
              )
        if cls == Campaign:
            self._loaded_campaigns.setdefault(
                pk,
                cls.objects.get(id=pk)
              )

    def prepare_datasets(self):
        """Query function, to retrive data and store it in memory in appropriate form:
        as result we will have list like
        {
            ds_id:campaign_id:
              {
                'clicks':[1, None, 3, 2]  <- list have the same length as labels list
                'impressions':[1,1,1,1]   <- the same lengt
              }
        }
        None value inside list means that for that date we have no data
        """

        labels_cnt = len(self._labels)
        query = Q(rec_date__range=(self._date_start, self._date_end))

        if self._datasources:
            query = query & Q(datasource__in=self._datasources)
        if self._campaigns:
            query = query & Q(campaign__in=self._campaigns)

        for click in Click.objects.filter(query):
            self.cache_fk_data(Datasource, click.datasource_id)
            self.cache_fk_data(Campaign, click.campaign_id)
            dict_ds_camp = self._datasets.setdefault(
                  (click.datasource_id, click.campaign_id),
                  {
                      'click': [None] * labels_cnt,
                      'impression': [None] * labels_cnt,
                  }
                )
            label_index = self._date_range[datetime.strftime(click.rec_date, DATE_FORMAT)]
            dict_ds_camp['click'][label_index] = click.amount

        for impression in Impression.objects.filter(query):
            self.cache_fk_data(Datasource, impression.datasource_id)
            self.cache_fk_data(Campaign, impression.campaign_id)
            dict_ds_camp = self._datasets.setdefault(
                  (impression.datasource_id, impression.campaign_id),
                  {
                      'click': [None] * labels_cnt,
                      'impression': [None] * labels_cnt,
                  }
                )
            label_index = self._date_range[datetime.strftime(impression.rec_date, DATE_FORMAT)]
            dict_ds_camp['impression'][label_index] = impression.amount

    def get_labels(self):
        """X-axis for Chartjs"""
        return self._labels

    def get_data(self):
        """List of lists, with number required by Chartjs to build lines"""
        result = []
        for k in self._datasets:
            result.append(self._datasets[k]['click'])
            result.append(self._datasets[k]['impression'])
        return result

    def get_providers(self):
        """Chartjs use this to build legend."""
        result = []
        for k in self._datasets:
            for metric_type in ['click', 'impression']:
                result.append("{}:{}:{}".format(
                    str(self._loaded_datasources.get(k[0], 'Unknown')),
                    str(self._loaded_campaigns.get(k[1], 'Unknown')),
                    metric_type)
                    )
        return result


index_view = IndexView.as_view()
adverity_data_json = AdverityDataJSONView.as_view()
