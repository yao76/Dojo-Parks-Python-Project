from django.db import models
from apps.login.models import *
import requests

class ParkManager(models.Manager):
    def address_validator(self, postData):
        errors = {}
        googlemapsapi = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': postData['location'],
            'sensor': 'false',
            'region': 'us',
            'key': 'AIzaSyDcuEo_YNfM-UN8VWL9IeXtfJHR30R4I_0'
        }
        req = requests.get(googlemapsapi, params=params)
        res = req.json()
        place_id = res['results'][0]['place_id']
        placesapi = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "key": "AIzaSyDcuEo_YNfM-UN8VWL9IeXtfJHR30R4I_0",
        }
        req2 = requests.get(placesapi, params=params)
        res2 = req2.json()
        title = res2['result']['name']
        all_parks = Park.objects.all()
        for park in all_parks:
            if title == park.title:
                errors['duplicate'] = "Park already exists"
        return errors


class Park (models.Model):
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    formatted_address = models.CharField(max_length=255)
    review = models.TextField()
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    longitude = models.DecimalField(max_digits=8, decimal_places=4)
    latitude = models.DecimalField(max_digits=8, decimal_places=4)
    operating_hours = models.TextField(blank=True)
    website = models.CharField(max_length=255, default="Sorry, no website found")
    phone_number = models.CharField(max_length=20, default="Sorry, no phone number found")
    created_by = models.ForeignKey(User, related_name="parks_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ParkManager()

