from django.db import models
""" This module contains model definition for adverity application """


class Datasource(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Campaign(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Click(models.Model):
    datasource = models.ForeignKey(Datasource, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    rec_date = models.DateTimeField('Date recorded')
    amount = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['rec_date', 'datasource', 'campaign'])
        ]


class Impression(models.Model):
    datasource = models.ForeignKey(Datasource, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    rec_date = models.DateTimeField('Date recorded')
    amount = models.FloatField(default=0.0)

    class Meta:
        indexes = [
            models.Index(fields=['rec_date', 'datasource', 'campaign'])
        ]
