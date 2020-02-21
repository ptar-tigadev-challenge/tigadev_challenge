from .models import Click
from .models import Impression

from django.db.models import Max
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from datetime import timedelta

DEFAULT_DATE_RANGE = 30
DATE_FORMAT = '%d/%m/%Y'

def get_date_from_model(date_start, date_end):
    """Get the latest model date and set it as end date.
    Move back DEFAULT_DATE_RANGE days and set it as start date"""
    if not date_end:
        max_impression_date = Impression.objects.all().aggregate(Max('rec_date'))['rec_date__max']
        if not max_impression_date:
            max_impression_date = timezone.make_aware(datetime.min)
        max_click_date = Click.objects.all().aggregate(Max('rec_date'))['rec_date__max']
        if not max_click_date:
            max_click_date = timezone.make_aware(datetime.min)

        date_end = max(max_impression_date, max_click_date)

    if not date_start:
        date_start = date_end - timedelta(days = DEFAULT_DATE_RANGE)
    return date_start, date_end

