from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField()
    content = models.CharField(max_length=20000)
    symbol = models.CharField(max_length=10)
    date = models.DateField()

