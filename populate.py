import os
import sys
import django
import random
sys.dont_write_bytecode = True




os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Vocabulary.settings')
django.setup()

from dictionary.models import Category,Dictionary





for d in Dictionary.objects.all():
    date = str(d.created)
    category,_ = Category.objects.get_or_create(title=date)
    d.category = category
    d.save()


    


