from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField()
    content = models.CharField(max_length=20000)
    symbol = models.CharField(max_length=10)
    date = models.DateField()

class StockTick(models.Model):
    symbol = models.CharField(max_length=10, unique_for_date='date')
    date = models.DateField()
    open = models.FloatField()
    close = models.FloatField()
    high  = models.FloatField()
    low = models.FloatField()
    volume = models.FloatField()

class StockInfo(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    isindex = models.BooleanField()
    name = models.CharField(max_length=200)
    sector = models.CharField(max_length=200)
    week52high  = models.FloatField()
    week52low = models.FloatField()

