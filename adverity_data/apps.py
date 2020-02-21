from django.apps import AppConfig


class AdverityDataConfig(AppConfig):
    name = 'adverity_data'
    default_campaigns = [
        'GDN RMKT - Prio 1 Offer',
        'Summer Offer 2019 - India'
        ]
    """List of campaigns to narrow default search results"""
