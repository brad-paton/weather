import ast
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from google.auth import credentials
import os
import requests
import subprocess
import WeatherLibrary as LIB


# Set up OpenWeatherMap API credentials
api_key = os.environ['OPENWEATHERMAPAPIKEY']
lat = 28.55
lon = -81.38

# Convert secret to JSON
gcred = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
gcred = ast.literal_eval(gcred)
gred = json.dumps(gcred)

# Authenticate with Google Sheets API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_dict(gcred,scope)
client = gspread.authorize(credentials)

spreadsheet_name = 'weather'

# Open the spreadsheet
spreadsheet = client.open(spreadsheet_name)

# Clear sheet
worksheet = spreadsheet.sheet1
worksheet.clear()

# Get the current weather data
url = f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={api_key}&units=imperial'
response = requests.get(url,timeout=30)
data = response.json()

# Extract the relevant information
current_weather = {
    'Date': LIB.convert_unix_to_eastern(data['current']['dt']),
    'Temperature': data['current']['temp'],
    'Humidity': data['current']['humidity'],
    'Description': data['current']['weather'][0]['description'],
    'Pressure': data['current']['pressure'],
    'WindSpeed': data['current']['wind_speed'],
    'WindDir': data['current']['wind_deg'],
    'Sunrise': LIB.convert_unix_to_eastern(data['current']['sunrise']),
    'Sunset': LIB.convert_unix_to_eastern(data['current']['sunset']),
    'FeelsLike' : data['current']['feels_like'],
    'UVIndex' : data['current']['uvi']
}

# Update the Google Sheet with the current weather data and time
worksheet.append_row(list(current_weather.values()))

# Append current data to CSV
current_weather_url = 'https://raw.githubusercontent.com/brad-paton/weather/main/Weather.csv'

LIB.concat_weather(current_weather_url, current)

subprocess.run(['git', 'add', 'Weather.csv'])
commitmessage = "Updated CSV"
subprocess.run(['git', 'commit', '-m', commitmessage])
subprocess.run(['git', 'push'])

# Get the forecast data
url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=imperial'
response = requests.get(url,timeout=30)
data = response.json()

# Extract the relevant forecast information
forecast = []
for forecast_item in data['list']:

    forecast_data = {
        'Date': LIB.convert_unix_to_eastern(forecast_item['dt']),
        'Temperature': forecast_item['main']['temp'],
        'Humidity': forecast_item['main']['humidity'],
        'Description': forecast_item['weather'][0]['description'],
        'Pressure' : forecast_item['main']['pressure'],
        'WindSpeed': forecast_item['wind']['speed'],
        'WindDir': forecast_item['wind']['deg'],
        'Sunrise': 0,
        'Sunset': 0,
        'FeelsLike' : forecast_item['main']['feels_like'],
        'UVIndex' : 0
    }
    forecast.append(forecast_data)

# Update the Google Sheet with the forecast data
for forecast_data in forecast:
    worksheet.append_row(list(forecast_data.values()))
