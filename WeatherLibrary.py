from datetime import datetime
import pandas as pd
import pytz

def convert_unix_to_eastern(unix):
    utc_time = datetime.utcfromtimestamp(unix)
    utc_time = utc_time.replace(tzinfo=pytz.utc) #Set the timezone for UTC
    eastern = pytz.timezone('US/Eastern') #Define the Eastern timezone
    eastern_time = utc_time.astimezone(eastern) #Convert the UTC time to Eastern Time
    formatted_time = eastern_time.strftime('%Y-%m-%d %H:%M') # Format the datetime as a string
    return formatted_time

def concat_weather(csv_url, weather_list):
    df_current = pd.read_csv(csv_url) # Import CSV from url
    df_new = pd.DataFrame(weather_list) # Turn current weather into pandas data frame
    df_concatenated = pd.concat([df_current, df_new]) # Append to data frame
    csv_concatenated = df_concatenated.to_csv('Current_Weather.csv', index = False) # Turn dataframe into csv
    return csv_concatenated
