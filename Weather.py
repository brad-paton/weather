import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.auth import credentials
import os
import requests
from datetime import datetime
import pytz


# Set up OpenWeatherMap API credentials
api_key = 'd8803f200694590d01f64d045af4efcf'
city = 'Orlando,US'

# Set up Google Sheets credentials
credentials = GOOGLE_APPLICATION_CREDENTIALS

# Authenticate with Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials,scope)
client = gspread.authorize(credentials)

def convert_unix_to_eastern(unix):
    utc_time = datetime.utcfromtimestamp(unix)

    # Set the timezone for UTC
    utc_time = utc_time.replace(tzinfo=pytz.utc)

    # Define the Eastern timezone
    eastern = pytz.timezone('US/Eastern')

    # Convert the UTC time to Eastern Time
    eastern_time = utc_time.astimezone(eastern)

    # Format the datetime as a string
    formatted_time = eastern_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    print(formatted_time)
    
    return formatted_time


spreadsheet_name = 'weather'

# Open the spreadsheet
spreadsheet = client.open(spreadsheet_name)

# Clear existing worksheet data
worksheet = spreadsheet.sheet1
worksheet.clear()

# Get the current weather data
url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial'
response = requests.get(url,timeout=15)
data = response.json()


# Convert current time to Eastern Time Zone
current_time = datetime.now(pytz.utc)
eastern_timezone = pytz.timezone('US/Eastern')
current_time_eastern = current_time.astimezone(eastern_timezone)

# Extract the relevant information
current_weather = {
    'Date': convert_unix_to_eastern(data['dt']),
    'Temperature': data['main']['temp'],
    'Humidity': data['main']['humidity'],
    'Description': data['weather'][0]['description'],
    'Pressure': data['main']['pressure'],
    'WindSpeed': data['wind']['speed'],
    'WindDir': data['wind']['deg'],
    'Sunrise': convert_unix_to_eastern(data['sys']['sunrise']),
    'Sunset': convert_unix_to_eastern(data['sys']['sunset'])

}
print(type(current_weather['Date']))

# Update the Google Sheet with the current weather data and time
worksheet.append_row(list(current_weather.values()))

# Get the forecast data
url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=imperial'
response = requests.get(url,timeout=15)
data = response.json()

# Extract the relevant forecast information
forecast = []
for forecast_item in data['list']:
    forecast_time = datetime.strptime(forecast_item['dt_txt'], '%Y-%m-%d %H:%M:%S')
    forecast_time_eastern = forecast_time.astimezone(eastern_timezone)
    
    forecast_data = {
        'Date': forecast_time_eastern.strftime('%Y-%m-%d %H:%M:%S'),
        'Temperature': forecast_item['main']['temp'],
        'Humidity': forecast_item['main']['humidity'],
        'Description': forecast_item['weather'][0]['description']
    }
    forecast.append(forecast_data)

# Update the Google Sheet with the forecast data

for forecast_data in forecast:
    worksheet.append_row(list(forecast_data.values()))

print('Weather data and forecast have been stored in the Google Sheet.')
