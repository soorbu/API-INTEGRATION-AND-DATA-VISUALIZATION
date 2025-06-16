# views.py
import requests
import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from collections import Counter
import base64
from io import BytesIO

# setting style of chart appearance
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def weather_dashboard(request):
    """
    Main dashboard view that fetches weather data and renders the template
    """
    # get location from request parameters
    location = request.GET.get('location', 'London')     # default set to london
    
    # WeatherAPI configuration
    api_key = settings.WEATHER_API_KEY  # hidden key in settings.py
    base_url = "http://api.weatherapi.com/v1"
    
    try:
        # fetch current weather and forecast data
        weather_data = fetch_weather_data(api_key, base_url, location)
        
        # handling the error which might be raised in fetch_weather_data 
        if not weather_data:
            return render(request, 'error.html', {
                'error': 'Unable to fetch weather data'
            })
        
        # process data for charts and generate chart images
        chart_data = process_chart_data(weather_data)
        chart_images = generate_chart_images(weather_data)
        
        # extract timezone information for JavaScript
        location_tz = weather_data.get('location', {}).get('tz_id', 'UTC')
        location_local_time = weather_data.get('location', {}).get('localtime', '')
        
        context = {
            'weather_data': weather_data,
            'location_timezone': location_tz,
            'location_local_time': location_local_time,
            'chart_images': chart_images,
            **chart_data
        }
        return render(request, 'dashboard.html', context)
        
    except Exception as e:
        return render(request, 'error.html', {
            'error': f'Error fetching weather data: {str(e)}'
        })

def fetch_weather_data(api_key, base_url, location, days=5):
    """
    Fetch weather data from WeatherAPI
    """
    try:
        # current weather and forecast endpoint
        url = f"{base_url}/forecast.json"
        params = {
            'key': api_key,
            'q': location,
            'days': days,
            'aqi': 'yes', 
            'alerts': 'no'
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

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
        
        # process forecast data for multi-day charts
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
        
        # count weather conditions for pie chart
        condition_counter = Counter(condition_list)
        condition_labels = list(condition_counter.keys())
        condition_counts = list(condition_counter.values())
        
        return {
            'hourly_data': {
                'labels': hourly_labels,
                'temps': hourly_temps,
                'feels_like': hourly_feels_like,
                'humidity': hourly_humidity,
                'pressure': hourly_pressure,
                'pm25': hourly_pm25,
                'no2': hourly_no2,
                'o3': hourly_o3,
            },
            'forecast_data': {
                'dates': forecast_dates,
                'max_temps': forecast_max_temps,
                'min_temps': forecast_min_temps,
                'avg_temps': forecast_avg_temps,
                'rain_chance': forecast_rain_chance,
            },
            'condition_data': {
                'labels': condition_labels,
                'counts': condition_counts,
            }
        }
        
    except Exception as e:
        print(f"Error processing chart data: {e}")
        return {}

def generate_chart_images(weather_data):
    """
    Generate chart images using matplotlib and return as base64 encoded strings
    """
    chart_data = process_chart_data(weather_data)
    if not chart_data:
        return {}
    
    chart_images = {}
    
    # Set the figure size and DPI for better quality
    plt.rcParams['figure.figsize'] = (12, 6)
    plt.rcParams['figure.dpi'] = 100
    
    try:
        # 1. 24-Hour Temperature Trend
        fig, ax = plt.subplots(figsize=(12, 6))
        
        hours = range(len(chart_data['hourly_data']['labels']))
        ax.plot(hours, chart_data['hourly_data']['temps'], 
               label='Temperature (°C)', color='#ff6b6b', linewidth=2, marker='o')
        ax.plot(hours, chart_data['hourly_data']['feels_like'], 
               label='Feels Like (°C)', color='#ffa726', linewidth=2, marker='s')
        
        ax.set_xlabel('Hour of Day', fontsize=12)
        ax.set_ylabel('Temperature (°C)', fontsize=12)
        ax.set_title('24-Hour Temperature Trend', fontsize=14, fontweight='bold')
        ax.set_xticks(hours[::2])  # Show every 2nd hour
        ax.set_xticklabels([chart_data['hourly_data']['labels'][i] for i in hours[::2]])
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        chart_images['temp_chart'] = fig_to_base64(fig)
        plt.close(fig)
        
        # 2. 5-Day Forecast
        fig, ax = plt.subplots(figsize=(12, 6))
        
        days = range(len(chart_data['forecast_data']['dates']))
        ax.plot(days, chart_data['forecast_data']['max_temps'], 
               label='Max Temp (°C)', color='#e57373', linewidth=2, marker='o')
        ax.plot(days, chart_data['forecast_data']['min_temps'], 
               label='Min Temp (°C)', color='#64b5f6', linewidth=2, marker='s')
        ax.plot(days, chart_data['forecast_data']['avg_temps'], 
               label='Avg Temp (°C)', color='#81c784', linewidth=2, marker='^')
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Temperature (°C)', fontsize=12)
        ax.set_title('5-Day Forecast', fontsize=14, fontweight='bold')
        ax.set_xticks(days)
        ax.set_xticklabels(chart_data['forecast_data']['dates'])
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        chart_images['forecast_chart'] = fig_to_base64(fig)
        plt.close(fig)
        
        # 3. Humidity & Pressure (Dual Y-axis)
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        hours = range(len(chart_data['hourly_data']['labels']))
        color1 = '#42a5f5'
        ax1.set_xlabel('Hour of Day', fontsize=12)
        ax1.set_ylabel('Humidity (%)', color=color1, fontsize=12)
        line1 = ax1.plot(hours, chart_data['hourly_data']['humidity'], 
                        color=color1, linewidth=2, marker='o', label='Humidity (%)')
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.set_xticks(hours[::2])
        ax1.set_xticklabels([chart_data['hourly_data']['labels'][i] for i in hours[::2]])
        
        ax2 = ax1.twinx()
        color2 = '#ab47bc'
        ax2.set_ylabel('Pressure (mb)', color=color2, fontsize=12)
        line2 = ax2.plot(hours, chart_data['hourly_data']['pressure'], 
                        color=color2, linewidth=2, marker='s', label='Pressure (mb)')
        ax2.tick_params(axis='y', labelcolor=color2)
        
        # Add legend
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left')
        
        ax1.set_title('Humidity & Pressure Trends', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        chart_images['humidity_chart'] = fig_to_base64(fig)
        plt.close(fig)
        
        # 4. Air Quality Trends
        fig, ax = plt.subplots(figsize=(12, 6))
        
        hours = range(len(chart_data['hourly_data']['labels']))
        ax.plot(hours, chart_data['hourly_data']['pm25'], 
               label='PM2.5 (μg/m³)', color='#ff7043', linewidth=2, marker='o')
        ax.plot(hours, chart_data['hourly_data']['no2'], 
               label='NO2 (μg/m³)', color='#5c6bc0', linewidth=2, marker='s')
        ax.plot(hours, chart_data['hourly_data']['o3'], 
               label='O3 (μg/m³)', color='#26a69a', linewidth=2, marker='^')
        
        ax.set_xlabel('Hour of Day', fontsize=12)
        ax.set_ylabel('Concentration (μg/m³)', fontsize=12)
        ax.set_title('Air Quality Trends', fontsize=14, fontweight='bold')
        ax.set_xticks(hours[::2])
        ax.set_xticklabels([chart_data['hourly_data']['labels'][i] for i in hours[::2]])
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        chart_images['aq_chart'] = fig_to_base64(fig)
        plt.close(fig)
        
        # 5. Weather Conditions Pie Chart (Bonus)
        if chart_data['condition_data']['labels']:
            fig, ax = plt.subplots(figsize=(4, 4))
            
            colors = sns.color_palette("husl", len(chart_data['condition_data']['labels']))
            wedges, texts, autotexts = ax.pie(chart_data['condition_data']['counts'], 
                                            labels=chart_data['condition_data']['labels'],
                                            colors=colors,
                                            autopct='%1.1f%%',
                                            startangle=90)
            
            ax.set_title('Weather Conditions Distribution', fontsize=14, fontweight='bold')
            
            chart_images['conditions_chart'] = fig_to_base64(fig)
            plt.close(fig)
    
    except Exception as e:
        print(f"Error generating chart images: {e}")
    
    return chart_images

def fig_to_base64(fig):
    """
    Convert matplotlib figure to base64 encoded string
    """
    buffer = BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', facecolor='white', dpi=100)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    return image_base64

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
