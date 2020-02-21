from logging import getLogger
from datetime import datetime
from datetime import timedelta
from datetime import date

from django.views.generic import TemplateView
from django.db.models import Q

from chartjs.views.lines import BaseLineChartView
from .models import Datasource
from .models import Campaign
from .models import Click
from .models import Impression

from .apps import AdverityDataConfig

from .forms import ParametersForm

from .date_util import DEFAULT_DATE_RANGE
from .date_util import DATE_FORMAT
from .date_util import get_date_from_model

class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = ParametersForm()
        dates = get_date_from_model(None, None)
        form.fields['date_start'].initial = dates[0].date
        form.fields['date_end'].initial =  dates[1].date
        context['form'] = form
        return context

def proceed_json_request(request):
    view = AdverityDataJSONView()
    return view


class AdverityDataJSONView(BaseLineChartView):
    def __init__(self,**kwargs):
        self._logger = getLogger(self.__class__.__name__)
        self._datasources = kwargs.get('datasources', None)
        self._campaigns = kwargs.get('campaigns', None)

        self._date_start, self._date_end = get_date_from_model(
                  kwargs.get('date_start', None),
                  kwargs.get('date_end', None)
            )
        self._datasources = None
        self._campaigns = Campaign.objects.filter(name__in=AdverityDataConfig.default_campaigns)

        self._date_range = {}
        self._datasets = {}
        self._loaded_datasources = {}
        self._loaded_campaigns = {}

    def post(self, request, *args, **kwargs):
        return self.get(request, args, kwargs)

    def generate_date_range(self, date_start, date_end):
        new_date = date_start
        index = 0
        while new_date <= date_end:
            self._date_range[datetime.strftime(new_date, DATE_FORMAT)] = index
            index = index + 1
            new_date = new_date + timedelta(days=1)
        self._labels = list(self._date_range.keys())

    def cache_fk_data(self, cls, pk):
        if cls == Datasource:
            self._loaded_datasources.setdefault(pk,
              cls.objects.get(id=pk)
            )
        if cls == Campaign:
            self._loaded_campaigns.setdefault(pk,
              cls.objects.get(id=pk)
            )
    def prepare_datasets(self):
        labels_cnt = len(self._labels)
        query = Q(rec_date__range=(self._date_start, self._date_end))# & Q(campaign_id__exact=1030)

        if self._datasources:
            query = query & Q(datasource__in=self._datasources)
        if self._campaigns:
            query = query & Q(campaign__in=self._campaigns)
        for click in Click.objects.filter(query):
            self.cache_fk_data(Datasource, click.datasource_id)
            self.cache_fk_data(Campaign, click.campaign_id)
            dict_ds_camp = self._datasets.setdefault((click.datasource_id, click.campaign_id),
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
            dict_ds_camp = self._datasets.setdefault((impression.datasource_id, impression.campaign_id),
                          {
                              'click': [None] * labels_cnt,
                              'impression': [None] * labels_cnt,
                          }
                          )
            label_index = self._date_range[datetime.strftime(impression.rec_date, DATE_FORMAT)]
            dict_ds_camp['impression'][label_index] = impression.amount


    def get_context_data(self, **kwargs):
        context = super(BaseLineChartView, self).get_context_data(**kwargs)
        if self.request.method == 'POST':
            form = ParametersForm(self.request.POST)
            if form.is_valid():
                self._date_start = form.cleaned_data['date_start']
                print(form.cleaned_data['date_start'])

                self._date_end = form.cleaned_data['date_end']
                self._datasources = form.cleaned_data['datasources']
                self._campaigns = form.cleaned_data['campaigns']
            else:
                print(form.errors)
        self.generate_date_range(self._date_start, self._date_end)
        self.prepare_datasets()
        context.update({"labels":self.get_labels(), 'datasets': self.get_datasets()})
        return context

    def get_labels(self):
        return self._labels

    def get_data(self):
        result = []
        for k in self._datasets:
            result.append(self._datasets[k]['click'])
            result.append(self._datasets[k]['impression'])
        return result

    def get_providers(self):
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
