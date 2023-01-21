import requests
from geopy.distance import distance
from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from star_burger.settings import GEOCODER_API_KEY
from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem, Place


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()["response"]["GeoObjectCollection"]["featureMember"]

    if not found_places:
        raise requests.exceptions.RequestException

    most_relevant = found_places[0]
    lon, lat = most_relevant["GeoObject"]["Point"]["pos"].split(" ")
    return lat, lon


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.all()\
        .exclude(order_status='handled')\
        .calculate_order_cost()\
        .prefetch_related(
            'order_products__product',
            'cooking_restaurant',
            'place'
        )\
        .order_by('-order_status')
    all_restaurants = Restaurant.objects.all()
    unavailable_restaurants_menu = RestaurantMenuItem.objects.filter(availability=False)\
        .prefetch_related('restaurant', 'product')\
        .values('restaurant', 'product', 'availability')
    for order in orders:
        products_in_order = [product.product.id for product in order.order_products.all()]
        unavailable_products_in_restaurants = [
            item for item in unavailable_restaurants_menu
            if item['product'] in products_in_order
        ]
        unavailable_restaurants = [item['restaurant'] for item in unavailable_products_in_restaurants]
        available_restaurants = [
            restaurant for restaurant in all_restaurants
            if restaurant.id not in unavailable_restaurants
        ]

        if order.place:
            order_lat = order.place.lat
            order_lon = order.place.lon
        else:
            try:
                order_coordinates = fetch_coordinates(GEOCODER_API_KEY, order.address)
            except requests.exceptions.RequestException:
                distance_to_available_restaurants = [
                    {'name': restaurant.name, 'distance': None}
                    for restaurant in available_restaurants
                ]
                order.available_restaurants = distance_to_available_restaurants
                continue

            order_lat, order_lon = order_coordinates
            order.place, _ = Place.objects.get_or_create(
                address=order.address,
                lat=order_lat,
                lon=order_lon
            )
            order.save()

        distance_to_available_restaurants = [
            {
                'name': restaurant.name,
                'distance': round(
                    distance(
                        (order_lat, order_lon),
                        (restaurant.lat, restaurant.lon)
                    ).km, 3
                )
            }
            for restaurant in available_restaurants
        ]
        order.available_restaurants = distance_to_available_restaurants

    return render(request, template_name='order_items.html', context={
        'orders': orders
    })
