from django.urls import path

from . import views

urlpatterns = [
    path('',
         views.index_view,
         name='index_view'
         ),
    path('adverity_data_json',
         views.adverity_data_json,
         name='adverity_data_json'
         ),
]
