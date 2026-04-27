from django.db import models

# Create your models here.
from django.db import models
from brands.models import BrandProfile

class Campaign(models.Model):
    brand = models.ForeignKey(BrandProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50, default='open')
    deadline = models.DateField()
    budget_range = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    #Here we didn't defined primary key for Campaign bcz in
    #Djnago automatically create one for us-> id = models.AutoField(primary_key=True)
from influencers.models import InfluencerProfile

class Application(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    influencer = models.ForeignKey(InfluencerProfile, on_delete=models.CASCADE)

    status = models.CharField(max_length=50, default='pending')
    message = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class Review(models.Model):
    # Ek application ka ek hi review ho sakta hai
    application = models.OneToOneField('Application', on_delete=models.CASCADE, related_name='review')
    
    # Kisne review diya (Reviewer)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    
    # Kise review mila (Reviewee)
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.username} -> {self.reviewee.username} ({self.rating}★)"