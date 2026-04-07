from django.db import models

# Create your models here.
from django.db import models
from campaigns.models import Application

class Collaboration(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    terms = models.TextField()
    started_at = models.DateTimeField(auto_now_add=True)