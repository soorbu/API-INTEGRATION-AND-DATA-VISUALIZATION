# views.py
import requests
import json
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from collections import Counter

def weather_dashboard(request):
    """
    Main dashboard view that fetches weather data and renders the template
    """
    # Get location from request parameters or default to London
    location = request.GET.get('location', 'London')
    
    # WeatherAPI configuration
    api_key = settings.WEATHER_API_KEY  # hidden key in settings.py
    base_url = "http://api.weatherapi.com/v1"
    
    try:
        # Fetch current weather and forecast data
        weather_data = fetch_weather_data(api_key, base_url, location)
        
        # handling the error which might be raised in fetch)weather_data 
        if not weather_data:
            return render(request, 'error.html', {
                'error': 'Unable to fetch weather data'
            })
        
        # Process data for charts
        chart_data = process_chart_data(weather_data)
        # Extract timezone information for JavaScript
        location_tz = weather_data.get('location', {}).get('tz_id', 'UTC')
        location_local_time = weather_data.get('location', {}).get('localtime', '')
        
        context = {
            'weather_data': weather_data,
            'location_timezone': location_tz,
            'location_local_time': location_local_time,
            **chart_data
        }
        return render(request, 'dashboard.html', context)
        
    except Exception as e:
        return render(request, 'error.html', {
            'error': f'Error fetching weather data: {str(e)}'
        })

def fetch_weather_data(api_key, base_url, location, days=5):
    """
    Fetch weather the data from WeatherAPI
    """
    try:
        # Current weather and forecast endpoint
        url = f"{base_url}/forecast.json"
        params = {
            'key': api_key,
            'q': location,
            'days': days,
            'aqi': 'yes', 
            'alerts': 'no'
        }

        # the request url should look like baseurl&q=London&days=5&aqi=yes&alerts=no
        # timeout of 10 sec ensures the page will raise Timeout exception if weather api servers don't respond within 10sec
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # raise exceptions imediately when http gives error response
        
        return response.json()          # return the json to weather dashboard funtion 
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None         # print error and do nothing 

def process_chart_data(weather_data):
    """
    Process raw weather data for chart visualization
    """
    try:
        # get today's hourly data (first 24 hours)
        hourly_data = weather_data['forecast']['forecastday'][0]['hour']
        forecast_days = weather_data['forecast']['forecastday']
        
        # process hourly data for 24-hour charts
        hourly_labels = []
        hourly_temps = []
        hourly_feels_like = []
        hourly_humidity = []
        hourly_pressure = []
        hourly_pm25 = []
        hourly_no2 = []
        hourly_o3 = []
        
        for hour in hourly_data:
            # format time for labels
            time_obj = datetime.strptime(hour['time'], '%Y-%m-%d %H:%M')
            hourly_labels.append(time_obj.strftime('%H:%M'))
            
            hourly_temps.append(hour['temp_c'])
            hourly_feels_like.append(hour['feelslike_c'])
            hourly_humidity.append(hour['humidity'])
            hourly_pressure.append(hour['pressure_mb'])
            
            # air quality data
            if 'air_quality' in hour:
                hourly_pm25.append(hour['air_quality']['pm2_5'])
                hourly_no2.append(hour['air_quality']['no2'])
                hourly_o3.append(hour['air_quality']['o3'])
            else:
                hourly_pm25.append(0)
                hourly_no2.append(0)
                hourly_o3.append(0)
        
        # Process forecast data for multi-day charts
        forecast_dates = []
        forecast_max_temps = []
        forecast_min_temps = []
        forecast_avg_temps = []
        forecast_rain_chance = []
        condition_list = []
        
        for day in forecast_days:
            # Format date for labels
            date_obj = datetime.strptime(day['date'], '%Y-%m-%d')
            forecast_dates.append(date_obj.strftime('%m/%d'))
            
            forecast_max_temps.append(day['day']['maxtemp_c'])
            forecast_min_temps.append(day['day']['mintemp_c'])
            forecast_avg_temps.append(day['day']['avgtemp_c'])
            forecast_rain_chance.append(day['day']['daily_chance_of_rain'])
            condition_list.append(day['day']['condition']['text'])
        
        # Count weather conditions for pie chart
        condition_counter = Counter(condition_list)
        condition_labels = list(condition_counter.keys())
        condition_counts = list(condition_counter.values())
        
        return {
            # Hourly data (JSON serialized for JavaScript)
            'hourly_labels': json.dumps(hourly_labels),
            'hourly_temps': json.dumps(hourly_temps),
            'hourly_feels_like': json.dumps(hourly_feels_like),
            'hourly_humidity': json.dumps(hourly_humidity),
            'hourly_pressure': json.dumps(hourly_pressure),
            'hourly_pm25': json.dumps(hourly_pm25),
            'hourly_no2': json.dumps(hourly_no2),
            'hourly_o3': json.dumps(hourly_o3),
            
            # Forecast data
            'forecast_dates': json.dumps(forecast_dates),
            'forecast_max_temps': json.dumps(forecast_max_temps),
            'forecast_min_temps': json.dumps(forecast_min_temps),
            'forecast_avg_temps': json.dumps(forecast_avg_temps),
            'forecast_rain_chance': json.dumps(forecast_rain_chance),
            
            # Weather conditions
            'condition_labels': json.dumps(condition_labels),
            'condition_counts': json.dumps(condition_counts),
        }
        
    except Exception as e:
        print(f"Error processing chart data: {e}")
        # Return empty data if processing fails
        return {
            'hourly_labels': json.dumps([]),
            'hourly_temps': json.dumps([]),
            'hourly_feels_like': json.dumps([]),
            'hourly_humidity': json.dumps([]),
            'hourly_pressure': json.dumps([]),
            'hourly_pm25': json.dumps([]),
            'hourly_no2': json.dumps([]),
            'hourly_o3': json.dumps([]),
            'forecast_dates': json.dumps([]),
            'forecast_max_temps': json.dumps([]),
            'forecast_min_temps': json.dumps([]),
            'forecast_avg_temps': json.dumps([]),
            'forecast_rain_chance': json.dumps([]),
            'condition_labels': json.dumps([]),
            'condition_counts': json.dumps([]),
        }

def search_locations(request):
    """
    API endpoint to search for locations
    """
    query = request.GET.get('q', '')
    
    if not query:
        return JsonResponse({'results': []})
    
    api_key = settings.WEATHER_API_KEY
    base_url = "http://api.weatherapi.com/v1"
    
    try:
        url = f"{base_url}/search.json"
        params = {
            'key': api_key,
            'q': query
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        locations = response.json()
        
        return JsonResponse({'results': locations})
        
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            'results': [],
            'error': str(e)
        })