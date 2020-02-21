from logging import getLogger
from datetime import datetime
from datetime import timedelta

from django.views.generic import TemplateView
from django.db.models import Max
from django.db.models import Q
from django.utils import timezone

from chartjs.views.lines import BaseLineChartView
from .models import Click
from .models import Impression
from .forms import ParametersForm

DEFAULT_DATE_RANGE = 30
DATE_FORMAT = '%d/%m/%Y'
class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ParametersForm()
        return context

class AdverityDataJSONView(BaseLineChartView):
    def __init__(self,**kwargs):
        self._logger = getLogger(self.__class__.__name__)
        self._datasources = kwargs.get('datasources', None)
        self._campaigns = kwargs.get('campaigns', None)

        self._date_start = kwargs.get('date_start', None)
        self._date_end = kwargs.get('date_end', None)
        if not self._date_end:
            max_impression_date = Impression.objects.all().aggregate(Max('rec_date'))['rec_date__max']
            if not max_impression_date:
                max_impression_date = timezone.make_aware(datetime.min)
            max_click_date = Click.objects.all().aggregate(Max('rec_date'))['rec_date__max']
            if not max_click_date:
                max_click_date = timezone.make_aware(datetime.min)

            self._date_end = max(max_impression_date, max_click_date)
        if not self._date_start:
            self._date_start = self._date_end - timedelta(days = DEFAULT_DATE_RANGE)
        self._date_range = {}
        self._datasets = {}

    def generate_date_range(self, date_start, date_end):
        new_date = date_start
        index = 0
        while new_date <= date_end:
            self._date_range[datetime.strftime(new_date, DATE_FORMAT)] = index
            index = index + 1
            new_date = new_date + timedelta(days=1)
        self._labels = list(self._date_range.keys())

    def prepare_datasets(self):
        labels_cnt = len(self._labels)
        q_date_range = Q(rec_date__range=(self._date_start, self._date_end))# & Q(campaign_id__exact=1030)
        for click in Click.objects.filter(q_date_range):
            dict_ds_camp = self._datasets.setdefault((click.datasource_id, click.campaign_id),
                          {
                              'click': [None] * labels_cnt,
                              'impression': [None] * labels_cnt
                          }
                          )
            label_index = self._date_range[datetime.strftime(click.rec_date, DATE_FORMAT)]
            dict_ds_camp['click'][label_index] = click.amount


    def get_context_data(self, **kwargs):
        context = super(BaseLineChartView, self).get_context_data(**kwargs)
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
        return result

    def get_providers(self):
        result = []
        for k in self._datasets:
            result.append("{}:{}".format(k[0], k[1]))
        return result

index_view = IndexView.as_view()
adverity_data_json = AdverityDataJSONView.as_view()
