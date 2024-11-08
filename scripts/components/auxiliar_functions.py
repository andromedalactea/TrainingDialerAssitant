import os 

def absolute_path(relative_path):
    return os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), relative_path))     

import datetime
import pytz

def convert_timestamp_to_date(timestamp_str):
    # Convert the string to an integer (in milliseconds)
    timestamp_ms = int(timestamp_str)
    
    # Convert to seconds (since Python works with timestamps in seconds)
    timestamp_s = timestamp_ms / 1000
    
    # Define the New York timezone using pytz
    ny_tz = pytz.timezone('America/New_York')
    
    # Convert the timestamp (in UTC) to a UTC datetime object
    utc_datetime = datetime.datetime.utcfromtimestamp(timestamp_s)
    
    # Convert the UTC time to New York time
    ny_datetime = utc_datetime.replace(tzinfo=pytz.utc).astimezone(ny_tz)
    
    # Format the date and time without decimal places for the seconds (using strftime)
    formatted_datetime = ny_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    # Return the formatted date and time as a string
    return formatted_datetime