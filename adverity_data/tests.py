from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from .models import Datasource
from .models import Campaign
from .models import Click
from .models import Impression

class AdverityDataJSONViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        datasource = Datasource.objects.create(name = 'test datasource')
        campaign = Campaign.objects.create(name = 'test campaign')
        click = Click.objects.create(datasource = datasource,
            campaign = campaign,
            rec_date = datetime.now(),
            amount = 1
        )

    def test_no_parameters(self):
        response = self.client.get(reverse('adverity_data_json'))
        self.assertEqual(response.status_code, 200)
        print(response.context)
        self.assertTrue(len(response.context['labels'])==1)
