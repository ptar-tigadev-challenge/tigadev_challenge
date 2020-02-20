import os
import pandas as pd
import django
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tigadev_challenge.settings")
django.setup()
from adverity_data.models import Datasource
from adverity_data.models import Campaign
from adverity_data.models import Click
from adverity_data.models import Impression

DATE_FORMAT = '%d.%m.%Y'

def get_dimension_obj(cls, name, current):
    if not name:
        return None
    if current and current.name == name:
        return current
    else:
        return cls.objects.get_or_create(name=name)[0]

def new_metric(cls, datasource, campaign, date, value):
    if pd.isna(value):
        print('{} are None for date {}'.format(cls.__name__, record.Date))
    else:
        obj = cls(
            rec_date = datetime.strptime(date, DATE_FORMAT),
            datasource = datasource,
            campaign = campaign,
            amount = value
            )
        return obj

if __name__ == '__main__':
  df = pd.read_csv('test_data/input_data.csv')
  print(df)

  datasource = None
  campaign = None

  Click.objects.all().delete()
  Impression.objects.all().delete()

  clicks = []
  impressions = []

  for index, record in df.iterrows():
    datasource = get_dimension_obj(Datasource, record.Datasource, datasource)
    if not datasource:
        print('Error: missed datasource at record {}'.format(index))
        continue

    campaign = get_dimension_obj(Campaign, record.Campaign, campaign)
    if not campaign:
        print('Error: missed campaign at record {}'.format(index))
        continue

    click = new_metric(Click, datasource, campaign, record.Date, record.Clicks)
    if click:
        clicks.append(click)

    impression = new_metric(Impression, datasource, campaign, record.Date, record.Impressions)
    if impression:
        impressions.append(impression)


  Click.objects.bulk_create(clicks) #TODO Check chunk size
  Impression.objects.bulk_create(impressions)
