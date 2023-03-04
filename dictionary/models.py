from django.db import models
from datetime import date

# Create your models here.
class Dictionary(models.Model):
    # lang = models.CharField(max_length=5,choices=(('en','en'),('uz','uz')),default='en')
    word = models.CharField(max_length=150)
    meaning = models.CharField(max_length=300)
    created = models.DateField(default=date.today())
    example = models.CharField(max_length=500,blank=True,null=True)
    class Meta:
        ordering = ('-created',)