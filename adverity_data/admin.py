from django.contrib import admin
from .models import Datasource
from .models import Campaign
from .models import Click
from .models import Impression

admin.site.register(Datasource)
admin.site.register(Campaign)
admin.site.register(Click)
admin.site.register(Impression)

