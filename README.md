# Task 1: API INTEGRATION AND DATA VISUALIZATION 

*COMPANY*:  COTECH IT SOLUTIONS

*NAME*:  SURABHI SANJAY KHATALE

*INTERN ID*:  CT04DG167

*DOMAIN*:  PYTHON PROGRAMMING 

*MENTOR*:  VAISHALI SHRIVASTAVA

*DESCRIPTION*--

This is a Django-based Weather Dashboard that fetches and visualizes current weather, air quality data, and 5-day forecasts for any global location using the [WeatherAPI](https://www.weatherapi.com/). The dashboard includes interactive plots, real-time statistics, and intuitive charts rendered using Matplotlib and Seaborn.

---

## Features

- **Global location search**
- **24-hour temperature trends**
- **"Feels Like" vs actual temperature**
- **Humidity & Pressure dual-axis chart**
- **Air quality trends for PM2.5, NO₂, and O₃**
- **5-day weather forecast with highs/lows**
- **Weather condition distribution (pie chart)**
- **Intelligent timezone and local time handling**

---

## Screenshots of dashboard

![Image](https://github.com/user-attachments/assets/50a12356-62d7-4f9d-88b2-aeafa43fdd28)
![Image](https://github.com/user-attachments/assets/fb8b1654-30b2-41d2-be8d-e355b4b58b4a)
![Image](https://github.com/user-attachments/assets/634eb28b-4996-4494-ae75-40a1dc54a814)
![Image](https://github.com/user-attachments/assets/28b79f7a-5a1d-45b0-bba9-91d1c21dbb6a)

##  Project Structure

```
weather_dashboard/
├── weatherapp/
│   ├── templates/
│   │   └── dashboard.html
│   ├── views.py
│   ├── urls.py
│   ├── static/
│   └── ...
├── db.sqlite3
├── .env
├── manage.py
└── requirements.txt
```

---

## 🔧 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/weather_dashboard.git
cd weather_dashboard
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```
### 3. Add `.env` file

Create a `.env` file in the root directory:

```env
WEATHER_API_KEY=your_weatherapi_key_here
```

### 4. Run the server

```bash
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/` to use the dashboard.

---


##  Working

###  Location Search (`search_locations`)
AJAX endpoint that allows the user to type in a location and get real-time location suggestions via WeatherAPI's `/search.json`.

###  Data Fetching (`fetch_weather_data`)
Fetches:
- Current conditions
- 5-day forecast
- Hourly breakdown (24 hours)
- Air Quality (PM2.5, NO₂, O₃)

###  Chart Processing (`process_chart_data`)
Extracts structured data:
- Hourly temp, humidity, pressure
- Daily highs/lows/averages
- Air quality metrics
- Weather conditions (for pie chart)

###  Chart Generation (`generate_chart_images`)
Uses Matplotlib + Seaborn to render:
- Line charts (temperature, humidity, air quality)
- Dual Y-axis chart (humidity + pressure)
- Pie chart (weather types)

Images are encoded to Base64 and embedded into HTML templates.

---

##  Dependencies

- `Django`
- `requests`
- `matplotlib`
- `seaborn`
- `pandas`
- `numpy`
- `python-dotenv`

---




