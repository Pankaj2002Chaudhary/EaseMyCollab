from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Campaign, Application

admin.site.register(Campaign)
admin.site.register(Application)