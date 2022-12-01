from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
#from .restapis import related methods
from .models import CarModel
from .restapis import get_dealers_from_cf, get_request, post_request
from .restapis import get_dealer_by_id_from_cf, get_dealer_reviews_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successfully!")
            return redirect('djangoapp:index')
        else:
            messages.warning(request, "Invalid username or password.")
            return redirect("djangoapp:index")


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    print("Log out the user '{}'".format(request.user.username))
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['pass']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{}is not new user".format(username))
        if not user_exist:
            user = User.objects.create_user(
                username = username, first_name=first_name, last_name=last_name, password=password,)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/d2120f97-736e-4d71-bddf-0545ae090bf7/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        context = {}
        context["dealerships"] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {}
        dealer_url = "https://us-south.functions.appdomain.cloud/api/v1/web/d2120f97-736e-4d71-bddf-0545ae090bf7/dealership-package/get-dealership"
        dealer = get_dealer_by_id_from_cf(dealer_url, id=dealer_id)
 
        #print(dealer)
        context["dealer"] = dealer
    
        review_url = "https://us-south.functions.appdomain.cloud/api/v1/web/d2120f97-736e-4d71-bddf-0545ae090bf7/dealership-package/get-review"
        reviews = get_dealer_reviews_from_cf(review_url, id=dealer_id)

        #print(reviews)
        context["reviews"] = reviews
        
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    context = {}
    dealer_url = "https://us-south.functions.appdomain.cloud/api/v1/web/d2120f97-736e-4d71-bddf-0545ae090bf7/dealership-package/get-dealership"
    dealer = get_dealer_by_id_from_cf(dealer_url, id=dealer_id)
    context["dealer"] = dealer
    if request.method == 'GET':
        print("Entra en la view por GET")
        cars = CarModel.objects.all()
        context["cars"] = cars
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == 'POST':
        print("Entra en la view por POST")
        if request.user.is_authenticated:
            review = dict()
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            review["time"] = datetime.utcnow().isoformat()
            review["name"] = request.user.username
            review["dealership"] = dealer_id
            review["id"] = dealer_id
            review["review"] = request.POST["content"]
            review["purchase"] = False
            if "purchasecheck" in request.POST:
                if request.POST["purchasecheck"] == 'on':
                    review["purchase"] = True
            review["purchase_date"] = request.POST["purchasedate"]
            review["car_make"] = car.make.name
            review["car_model"] = car.name
            review["car_year"] = int(car.year.strftime("%Y"))
            print("--------------Review-------------")
            print(review)
            json_payload = {}
            json_payload["review"] = review
            print("--------------payload-------------")
            print(json_payload)
            review_post_url = "https://us-south.functions.appdomain.cloud/api/v1/web/d2120f97-736e-4d71-bddf-0545ae090bf7/dealership-package/post-review"
            post_request(review_post_url, json_payload, id=dealer_id)
            print("Request posted")
    return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
    #return redirect('djangoapp:index')
