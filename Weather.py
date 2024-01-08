import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime
import pytz

# Set up OpenWeatherMap API credentials
api_key = 'd8803f200694590d01f64d045af4efcf'
city = 'Orlando,US'

# Set up Google Sheets credentials
CRED = {
  "type": "service_account",
  "project_id": "weather-400602",
  "private_key_id": "d636c0cadc7172bf54b3b560207c5216e1bc01ea",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDA7BgpJFrcRXoV\nDAppjwcU5yh7JXsj/Dc5U5CDVo3uAXeVtQSz/gqsDvmY/T+ivcpydoihDbheICEy\nVRDqALYkreFgjd0OyGdu/5xNzYeB3S+A5+MAjOpOTyOpy379Dt4NCyTKBEoTT/d+\nNgcfnDCl2PlOLbw2LtWAILD/yAV7OuzyYZzBqNG99YQ88TzC4C4NijaCjOfAVLmL\n9RQ0b9Nm/s3Wyt4LVVgwOCucTjhddGMsQpVYX/Yqbace3Nvep/5oKx9oyA30L+td\nR5ElaUYMGGcVB3IQIMUMmyJ6YMbebBamGkF3xbhZlMXdbbxGpHAv2/pWhdm4xoHL\n2oPQ5S+ZAgMBAAECggEAF9dVaQgwHlaLrrwtMTxWsLOcYhOQszLBFFmKW2C/63DM\n+XhEW4YChZ7YI5rwWUlBEoIpglWyuhcYYyL2EyUBXWkLmCYP8nq7pZD7HPZQT7Eo\n5LJDcFb5wbGwA5S9XcKPmGcPJdP/34EbYcKFgNeJf4Vf0dR/FOcWxV3E4eczHjZE\nEPPsddqnID6WgghC68MwGh9QaUHrHHvkanlPwWvtMcZKcJO7F9DuA0rEL1906cwH\nzSrOrzmjSdOzP8qYh40+e/NVlqF3fqDh+PiyWGS3Khb6xyGmI1Vv93Fbg7tIB4Ua\nyupXE1u9XaBo6UaZHz9QsrPocCpXsIgRC9z0Oi4dMQKBgQDheOVWokniFPlEo2rw\nsidcTySR6eVClNqkhqf16KM2k6h7FE9P3MlePPVQvL0bVpDsjZwqSEljBTAwPP4d\ny+UacSZXKCdAMaGdVH6G450rAPBbh9dSSEpc1UOZWuM9Ld+KRje5CvdrO1Bgg2+h\niBNlcHj1BtKiZjLuWE8SMI/pdQKBgQDbCvszs5zbyAjF+xu+xeZ/lSJk4uzbXcQ1\nQAoBaf7qFkT2l63K0mgCyzAouLMFR9iyizkWghdRMdo10NZ7gBp6OileROTCQFjd\n7CBlmo2Q0wO7EmffpZZDZUp7h0TGo0Thl2LFL85/5u1cGZ7zBFhWYxHgW7fmF4Hb\nVQKzfrDFFQKBgQCLSKi79PMZQ4Wc3irA1/0yq/1WWhvzHotWmYyGf5jbrSmmJqy8\nFBMdMSEGKCHWEoriZrRy9kbHcbwMAJGmjH9R71YU/0wH/uDslPa4k0FTAHh6wpbE\nUL4HTQM+aAP6li0CeVAQ8nJXfsOva2J5cdsxjeJa00UpZ2LNFCZ8gR1VxQKBgALg\nsQ4r1Oq6RQs80k9+UBnq/qmupYf4QmSks7zzBItUwZEvyvO4Me+fdcGDM67lE768\nv4JBMUc6zXAZj0fOFgr3CqYXZ535tHEt8fsDvcpiS1FA26Z/iWrXQNRAobGuYXBJ\nSd3nU+IwSXwFRiZRL0vrP0fgTJk0Q9t60W9EQdRFAoGAYVJp3IPxETPb3vNgvW/0\nDlpdRVGbNY1qIHbfgp3f7BXKlaTpH9kGTPRNbHt/ulmd8RocXsMNWEjHi6w016hw\nAOCaJVZhMi0ARBA1zizGTc4kUfxUNP9dpHbg4Sh2qLlZNRCa5b2havK4UWAeltTl\n0zpk6dS8MXybE7kjZIbM/PE=\n-----END PRIVATE KEY-----\n",
  "client_email": "bradweather@weather-400602.iam.gserviceaccount.com",
  "client_id": "103687733476075062242",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/bradweather%40weather-400602.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

spreadsheet_name = 'weather'

# Authenticate with Google Sheets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_dict(CRED,scope)
client = gspread.authorize(credentials)

# Open the spreadsheet
spreadsheet = client.open(spreadsheet_name)

# Clear existing worksheet data
worksheet = spreadsheet.sheet1
worksheet.clear()

# Get the current weather data
url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial'
response = requests.get(url,timeout=15)
data = response.json()

# Extract the relevant information
current_weather = {
    'Temperature': data['main']['temp'],
    'Humidity': data['main']['humidity'],
    'Pressure': data['main']['pressure'],
    'Description': data['weather'][0]['description'],
    'WindSpeed': data['wind']['speed'],
    'WindDir': data['wind']['deg'],
    'Sunrise': data['sys']['sunrise'],
    'Sunset': data['sys']['sunset']

}

# Convert current time to Eastern Time Zone
current_time = datetime.now(pytz.utc)
eastern_timezone = pytz.timezone('US/Eastern')
current_time_eastern = current_time.astimezone(eastern_timezone)

# Update the Google Sheet with the current weather data and time
worksheet.append_row(list(current_weather.values()) + [current_time_eastern.strftime('%Y-%m-%d %H:%M:%S')])

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
        'Temperature': forecast_item['main']['temp'],
        'Humidity': forecast_item['main']['humidity'],
        'Description': forecast_item['weather'][0]['description'],
        'Date': forecast_time_eastern.strftime('%Y-%m-%d %H:%M:%S'),
    }
    forecast.append(forecast_data)

# Update the Google Sheet with the forecast data
#worksheet = spreadsheet.add_worksheet(title='Forecast', rows="100", cols="5")
#header_row = list(forecast[0].keys())
#worksheet.append_row(header_row)
for forecast_data in forecast:
    worksheet.append_row(list(forecast_data.values()))

print('Weather data and forecast have been stored in the Google Sheet.')
