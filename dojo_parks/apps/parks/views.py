from django.shortcuts import render, redirect, HttpResponseRedirect
from apps.parks.models import *
import requests
from django.http import JsonResponse
import json
from django.contrib import messages
from random import randint


# Create your views here.


def index(request):
    context = {
        "user" : User.objects.get(id=request.session["user_id"]),
        "all_parks": Park.objects.all(),
        "sidebar_parks": Park.objects.all().order_by("-id")[:10],
        "last_park": Park.objects.last(),
    }
    return render(request, 'parks/map.html', context)


def create(request):
    errors = Park.objects.address_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value, extra_tags = key)
        return redirect("/")
    else:
        # Google Maps API
        googlemapsapi = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': request.POST['location'],
            'sensor': 'false',
            'region': 'us',
            'key': 'AIzaSyDcuEo_YNfM-UN8VWL9IeXtfJHR30R4I_0',
        }
        req = requests.get(googlemapsapi, params=params)
        res = req.json()
        latitude = res['results'][0]['geometry']['location']['lat']
        longitude = res['results'][0]['geometry']['location']['lng']
        place_id = res['results'][0]['place_id']
        request.session['place_id'] = place_id

        # Google Places API
        placesapi = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "key": "AIzaSyDcuEo_YNfM-UN8VWL9IeXtfJHR30R4I_0",
        }
        req2 = requests.get(placesapi, params=params)
        res2 = req2.json()
        title = res2['result']['name']
        try:
            x = len(res2['result']['reviews'])
        except:
            review_text = "No reviews yet"
        try:
            review_text = res2['result']['reviews'][randint(1,x)]['text']
        except:
            review_text = "No reviews yet"
        try:
            website = res2['result']['website']
        except:
            website = "Sorry, no website available"
        try:
            rating = res2['result']['rating']
        except:
            rating = 0
        try:
            phone = res2['result']['formatted_phone_number']
        except:
            phone = "No Phone number available"
        try:
            hours = res2['result']['opening_hours']['weekday_text']
        except:
            hours = "No hours available"
        formatted_address = res2['result']['formatted_address']
        # Create the park 
        Park.objects.create(
            title=title,
            address=request.POST['location'],
            formatted_address=formatted_address,
            review=review_text,
            rating=rating,
            longitude=longitude,
            latitude=latitude,
            operating_hours=hours,
            website=website,
            phone_number=phone,
            created_by=User.objects.get(id=request.session["user_id"])
        )
        return redirect("/")

def parkinfo(request, parkid):
    park = Park.objects.get(id=parkid)
    hours_str = park.operating_hours #Get the string for park operating hours
    print(hours_str)
    if hours_str == "No hours available":
        left_bracket = "No hours listed"
        right_bracket= ""
        split_list = []
    else:
        split_list = hours_str.split(",") #Split the string into a list of strings, separated by commas

        #Replace [] and ' with empty string
        for word in split_list:
            if "[" in word:
                left_bracket = word.replace("[", "") #Only returns Monday without [
        for word in split_list:
            if "]" in word:
                right_bracket = word.replace("]", "") #Only returns Sunday without ]
        for word in split_list:
            if "'" in word:
                quotation = word.replace("'", "") #Not working
        
        split_list = split_list[1:-1]
    googlemapsapi = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': Park.objects.get(id=parkid).address,
        'sensor': 'false',
        'region': 'us',
        'key': 'AIzaSyDcuEo_YNfM-UN8VWL9IeXtfJHR30R4I_0'
    }
    req = requests.get(googlemapsapi, params=params)
    res = req.json()
    place_id = res['results'][0]['place_id']
    print(f"place id is {place_id}")
    placesapi = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "key": "AIzaSyDcuEo_YNfM-UN8VWL9IeXtfJHR30R4I_0",
    }
    req2 = requests.get(placesapi, params=params)
    res2 = req2.json()
    try:
        photo0 = res2['result']['photos'][0]['photo_reference']
    except:
        photo0 = ""
    try:
        photo1 = res2['result']['photos'][1]['photo_reference']
    except:
        photo1 = ""
    try:
        photo2 = res2['result']['photos'][2]['photo_reference']
    except:
        photo2 = ""

    
    context = {
        "selected_park": park,
        'photo0': photo0,
        'photo1': photo1,
        'photo2': photo2,
        "split_hours" : split_list,
        "formatted_hours" : left_bracket,
        "formatted_hours2" : right_bracket,
    }
    return render(request, "parks/parkinfo.html", context)


def removePark(request, parkid):
    x = Park.objects.get(id = parkid)
    if request.session['user_id'] == x.created_by.id :
        x.delete()
        return redirect('/')
    else:
        return redirect('/')

def darkmode(request):
    if "res1" not in request.session:
        request.session['res1'] = "Sorry no restaurants nearby"
        request.session['res2'] = ""
        request.session['res3'] = ""
    x = [request.session['res1'], request.session['res2'], request.session['res3']]
    context = {
        'nearby': x,
        "user" : User.objects.get(id=request.session["user_id"]),
        "all_parks": Park.objects.all(),
        "sidebar_parks": Park.objects.all().order_by("-id")[:10],
        "last_park": Park.objects.last(),
    }
    del(request.session['res1'])
    del(request.session['res2'])
    del(request.session['res3'])
    return render(request, "parks/darkmap.html", context)


def darkparkinfo(request, parkid):
    park = Park.objects.get(id=parkid)
    hours_str = park.operating_hours #Get the string for park operating hours
    print(hours_str)
    if hours_str == "No hours available":
        left_bracket = "No hours listed"
        right_bracket= ""
        split_list = []
    else:
        split_list = hours_str.split(",") #Split the string into a list of strings, separated by commas

        #Replace [] and ' with empty string
        for word in split_list:
            if "[" in word:
                left_bracket = word.replace("[", "") #Only returns Monday without [
        for word in split_list:
            if "]" in word:
                right_bracket = word.replace("]", "") #Only returns Sunday without ]
        for word in split_list:
            if "'" in word:
                quotation = word.replace("'", "") #Not working
        
        split_list = split_list[1:-1]
    googlemapsapi = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': Park.objects.get(id=parkid).address,
        'sensor': 'false',
        'region': 'us',
        'key': 'AIzaSyDcuEo_YNfM-UN8VWL9IeXtfJHR30R4I_0'
    }
    req = requests.get(googlemapsapi, params=params)
    res = req.json()
    place_id = res['results'][0]['place_id']
    print(f"place id is {place_id}")
    placesapi = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "key": "AIzaSyDcuEo_YNfM-UN8VWL9IeXtfJHR30R4I_0",
    }
    req2 = requests.get(placesapi, params=params)
    res2 = req2.json()
    try:
        photo0 = res2['result']['photos'][0]['photo_reference']
    except:
        photo0 = ""
    try:
        photo1 = res2['result']['photos'][1]['photo_reference']
    except:
        photo1 = ""
    try:
        photo2 = res2['result']['photos'][2]['photo_reference']
    except:
        photo2 = ""

    
    context = {
        "selected_park": park,
        'photo0': photo0,
        'photo1': photo1,
        'photo2': photo2,
        "split_hours" : split_list,
        "formatted_hours" : left_bracket,
        "formatted_hours2" : right_bracket,
    }
    return render(request, "parks/darkparkinfo.html", context)



def createdark(request):
    errors = Park.objects.address_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value, extra_tags = key)
        return redirect("/parks/darkmode")
    else:
        # Google Maps API
        googlemapsapi = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': request.POST['location'],
            'sensor': 'false',
            'region': 'us',
            'key': 'AIzaSyDcuEo_YNfM-UN8VWL9IeXtfJHR30R4I_0',
        }
        req = requests.get(googlemapsapi, params=params)
        res = req.json()
        latitude = res['results'][0]['geometry']['location']['lat']
        longitude = res['results'][0]['geometry']['location']['lng']
        place_id = res['results'][0]['place_id']
        request.session['place_id'] = place_id

        # Google Places API
        placesapi = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "key": "AIzaSyDcuEo_YNfM-UN8VWL9IeXtfJHR30R4I_0",
        }
        req2 = requests.get(placesapi, params=params)
        res2 = req2.json()
        title = res2['result']['name']
        try:
            x = len(res2['result']['reviews'])
        except:
            review_text = "No reviews yet"
        try:
            review_text = res2['result']['reviews'][randint(1,x)]['text']
        except:
            review_text = "No reviews yet"
        try:
            website = res2['result']['website']
        except:
            website = "Sorry, no website available"
        try:
            rating = res2['result']['rating']
        except:
            rating = 0
        try:
            phone = res2['result']['formatted_phone_number']
        except:
            phone = "No Phone number available"
        try:
            hours = res2['result']['opening_hours']['weekday_text']
        except:
            hours = "No hours available"
        formatted_address = res2['result']['formatted_address']
        # Create the park 
        Park.objects.create(
            title=title,
            address=request.POST['location'],
            formatted_address=formatted_address,
            review=review_text,
            rating=rating,
            longitude=longitude,
            latitude=latitude,
            operating_hours=hours,
            website=website,
            phone_number=phone,
            created_by=User.objects.get(id=request.session["user_id"])
        )
        return redirect("/parks/darkmode")

def removeParkDark(request, parkid):
    x = Park.objects.get(id = parkid)
    if request.session['user_id'] == x.created_by.id :
        x.delete()
        return redirect('/parks/darkmode')
    else:
        return redirect('/parks/darkmode')
    


def apis(request, lat, long):
    nearby = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{long}&radius=15000&type=restaurant&key=AIzaSyDcuEo_YNfM-UN8VWL9IeXtfJHR30R4I_0"
    req = requests.get(nearby)
    res = req.json()
    print(res)

    try:
        request.session['res1'] = res['results'][0]['name']
    except:
        request.session['res1'] = "No restaurants nearby"
    try:
        request.session['res2'] = res['results'][1]['name']
    except:
        request.session['res2'] = ""
    try:
        request.session['res3'] = res['results'][2]['name']
    except:
        request.session['res3'] = ""

    return redirect("/parks/darkmode")
    
    