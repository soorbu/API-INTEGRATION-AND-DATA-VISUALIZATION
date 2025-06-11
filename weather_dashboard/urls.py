from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('', views.weather_dashboard, name='dashboard'),
    path('api/search-locations/', views.search_locations, name='search_locations'),  # <-- ADD THIS
]
