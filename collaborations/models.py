from django.db import models

# Create your models here.
from django.db import models
from campaigns.models import Application
from django.contrib.auth import get_user_model

User = get_user_model()
class Collaboration(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    terms = models.TextField()
    started_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    campaign = models.ForeignKey('campaigns.Campaign', on_row=models.CASCADE)
    reviewer = models.ForeignKey(User, on_row=models.CASCADE, related_name='reviews_given')
    target_user = models.ForeignKey(User, on_row=models.CASCADE, related_name='reviews_received')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('campaign', 'reviewer', 'target_user') # Ek collab pe ek hi review