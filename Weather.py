import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.auth import credentials
import os
import requests
from datetime import datetime
import pytz


# Set up OpenWeatherMap API credentials
api_key = 'd8803f200694590d01f64d045af4efcf'
lat = 28.55
lon = -81.38

# Set up Google Sheets credentials
gcred = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')


# Authenticate with Google Sheets API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_dict(gcred,scope)
client = gspread.authorize(credentials)

def convert_unix_to_eastern(unix):
    utc_time = datetime.utcfromtimestamp(unix)

    utc_time = utc_time.replace(tzinfo=pytz.utc) #Set the timezone for UTC

    eastern = pytz.timezone('US/Eastern') #Define the Eastern timezone

    eastern_time = utc_time.astimezone(eastern) #Convert the UTC time to Eastern Time

    formatted_time = eastern_time.strftime('%Y-%m-%d %H:%M') # Format the datetime as a string

    print(formatted_time)

    return formatted_time


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
    'Date': convert_unix_to_eastern(data['current']['dt']),
    'Temperature': data['current']['temp'],
    'Humidity': data['current']['humidity'],
    'Description': data['current']['weather'][0]['description'],
    'Pressure': data['current']['pressure'],
    'WindSpeed': data['current']['wind_speed'],
    'WindDir': data['current']['wind_deg'],
    'Sunrise': convert_unix_to_eastern(data['current']['sunrise']),
    'Sunset': convert_unix_to_eastern(data['current']['sunset']),
    'FeelsLike' : data['current']['feels_like'],
    'UVIndex' : data['current']['uvi']
}

# Update the Google Sheet with the current weather data and time
worksheet.append_row(list(current_weather.values()))

# Get the forecast data
url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=imperial'
response = requests.get(url,timeout=30)
data = response.json()

# Extract the relevant forecast information
forecast = []
for forecast_item in data['list']:

    forecast_data = {
        'Date': convert_unix_to_eastern(forecast_item['dt']),
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

print('Weather data and forecast have been stored in the Google Sheet.')
