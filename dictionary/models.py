from django.db import models
from datetime import date

# Create your models here.



class Category(models.Model):
    title = models.CharField(max_length=255)


    
class Dictionary(models.Model):
    # lang = models.CharField(max_length=5,choices=(('en','en'),('uz','uz')),default='en')
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
    chat_id = models.PositiveIntegerField(default=764719178)
    word = models.CharField(max_length=150)
    meaning = models.CharField(max_length=300)
    created = models.DateField(default=date.today())
    example = models.CharField(max_length=500,blank=True,null=True)
    class Meta:
        ordering = ('-created',)