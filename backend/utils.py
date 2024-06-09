from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import pytz


# Returns True if the date is in the future in the local time of the location. 
def is_future_date(latitude, longitude, iso_date):
    timezone = pytz.timezone(infer_timezone(latitude,  longitude))
    current_date = datetime.now(timezone)
    given_date = datetime.fromisoformat(iso_date).astimezone(timezone)

    # Apparently there is delay in the api between archive and forecast.
    future_date_threshold = current_date - timedelta(days=2)
    
    return given_date > future_date_threshold

# Infer timezone from geospatial information. 
def infer_timezone(latitude, longitude):
    tf = TimezoneFinder()
    timezone_name = tf.timezone_at(lng=longitude, lat=latitude)
    return timezone_name