import sys
import requests
import xmltodict
from datetime import datetime   
from typing import List
from flask import Flask, request
import logging
import requests
import math


from geopy.geocoders import Nominatim
geocoder = Nominatim(user_agent='iss_tracker')

logging.basicConfig(level=logging.WARNING)
MEAN_EARTH_RADIUS = 6378.137 # in kilometers

app = Flask(__name__)

def get_data(alldata=False)->List[dict]:
    """
    Function gets and returns all of the ISS epoch data set.
    Args:
        None
    Returns:
        epoch_data (dict): a dictionary of all the ISS position/velocity/time data.
    """
    response = requests.get("https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS\
.OEM_J2K_EPH.xml")
    try:
        data_dict = xmltodict.parse(response.content)
    except:
        logging.critical("Ensure xml data file address is given. \n")
        sys.exit()
    try:
        epoch_data = data_dict['ndm']['oem']['body']['segment']['data']['stateVector']
    except:
        logging.critical("Recheck https address; cannot find correct data file. \n")
        sys.exit()
    if alldata==True:# only used for return comments, return header, return metadata
        return data_dict
    else:
        return epoch_data

@app.route('/comment', methods = ['GET'])
def return_comments()->List[dict]:
    """
    Function returns the comments written in the ISS data file. 
    Args: 
        None
    Returns:
        comments (list of dicts): a list of all the comments written, where each new line is written as a new dictionary.
    """
    all = get_data(True)
    comments = all['ndm']['oem']['body']['segment']['data']['COMMENT']
    return comments

@app.route('/header', methods = ['GET'])
def return_header()->dict:
    """
    Function returns the header written in the ISS data file:
    Args:
        None
    Returns:
        header (dict): dictionary of all items in the header. Each new line is a different key/val pair.
    """
    all = get_data(True)
    header = all['ndm']['oem']['header']
    return header

@app.route('/metadata', methods = ['GET'])
def return_meta_data()->dict:
    """
    Function returns the metadata about the ISS (written in the ISS data file) (has comments about ISS generally).
    Args:
        None
    Returns:
        metadata (dict): dictionary with information about the ISS's name, the time reference used, etc.
    """
    all = get_data(True)
    metadata = all['ndm']['oem']['body']['segment']['metadata']
    return metadata

@app.route('/epochs', methods = ['GET'])
def return_entire_dataset()->List[dict]:
    """
    Function uses flask commands to get the portions or all of the data set and return it to the terminal.
    Args:
        None
    Returns:
        data_dict (dict): a dictionary of all the ISS position/velocity/time data.
    """
    all_epochs = get_data()
    num_epochs = len(all_epochs)
    try:
        limit = int(request.args.get("limit", num_epochs)) # default is all data
    except ValueError:
        return "Invalid limit parameter; must be positive integer. \n"
    if limit<0:
         return "Invalid limit parameter; must be positive integer.\n"
     
    try:
        offset =int(request.args.get("offset", 0)) # default start at beginning of data
    except ValueError:
        return "Invalid offset parameter; must be positive integer. \n" 
    
    if offset<0:
        return "Invalid offset parameter; must be positive integer.\n"
    if limit == 0:
        return "No ISS data for given restrictions\n"

    list_of_dicts = all_epochs[offset: offset+limit]
    return list_of_dicts

@app.route('/epochs/<epoch>', methods = ['GET'])
def return_specific_epoch_data(epoch:str)->dict:
    """
    Function uses flask commands to return the ISS data at a specific epoch (time stamp is input by user).
    Args:
        epoch (str): an epoch time stamp, i.e: 2024-053T23:44:00.000Z (must be of this format). 
    Returns:
        each_epoch (dict): a dictionary of the ISS position and velocity at particular epoch.
        or, instead of each_epoch: a string stating "no data found."
    """
    epoch_data = get_data()
    for each_epoch in epoch_data:
        if each_epoch['EPOCH'] == epoch:
            return each_epoch
    return "No data found at particular epoch.\n"
   
@app.route('/epochs/<epoch>/speed', methods=['GET'])
def return_specific_epoch_instspeed(epoch:str)->dict:
    """
    Function uses flask commands to return the ISS speed at a specific epoch (time stamp is input by user).
    Args:
        epoch (str): an epoch time stamp, i.e: 2024-053T23:44:00.000Z (must be of this format). 
    Returns:
        return_V_dict (dict): a dictionary of the instantaneous ISS speed (with units) at the given time stamp.
        or, instead of return_V_dict: a string stating "no data found."
    """
    specific_epoch = return_specific_epoch_data(epoch)
    try:
        vx = float(specific_epoch["X_DOT"]["#text"])
    except TypeError:
        return "No data found at particular epoch. Cannot calculate instantaneous speed.\n"
    vy = float(specific_epoch["Y_DOT"]["#text"])
    vz = float(specific_epoch["Z_DOT"]["#text"])
    v = (vx**2 + vy**2 + vz**2) ** 0.5
    return_V_dict = {"instantaneous speed": v, "speed units" : specific_epoch["X_DOT"]["@units"]}
    return return_V_dict


@app.route('/epochs/<epoch>/location', methods=['GET'])
def return_location(epoch:str)->dict:
   """
   Function returns the latitude, longitude, altitude, and geoposition (which city the ISS is traveling over) for a given epoch/timestamp.
   Args:
       epoch (str): epoch string in UTC time, i.e. 2024-053T23:44:00.000Z (must be of t\
his format). 
   Returns:
       geodata (dictionary): contains the iss's position (x,y,z coordinates), the geodata (latitude, longitude, altitude, and gelocation), and the timestamp (particular input epoch).
   """
   epoch_data= return_specific_epoch_data(epoch)
   try:
      x = float(epoch_data["X"]["#text"])
   except:
      return "wrong input type/date \n"
   y = float(epoch_data["Y"]["#text"])
   z = float(epoch_data["Z"]["#text"])
   lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))
   alt = math.sqrt(x**2 + y**2 + z**2) - MEAN_EARTH_RADIUS
   
   date_part, time_part = epoch.split("T")
   hrs, mins, _ = time_part.split(":")
   lon = math.degrees(math.atan2(y, x)) - ((float(hrs)-12)+(float(mins)/60))*(360/24) + 19
   if lon > 180: lon = -180 + (lon - 180)
   if lon < -180: lon = 180 + (lon + 180)

    
   geoloc = geocoder.reverse((lat, lon), zoom=15, language='en')
    
   geo_data={"iss_position": {"x":x, "y":y, "z":z}, "geodata":{"latitude": lat, "longitude" : lon, "altitude":alt, "geolocation/city": str(geoloc)}, "timestamp":epoch}
   return geo_data
    

@app.route('/now', methods=['GET'])
def closest_epoch()->dict:
    """
    Function uses flask commands to return the ISS data at the current UTC time.
    Args:
        None
    Returns:
        return_vectors_speed (dict): a dictionary of the instantaneous ISS speed (with units) \
            at the closest time stamp (to the current time).
    """
    curr_time = str(datetime.utcnow())
    print("Current UTC time is:", curr_time)
    # curr_time = "2024-02-13 12:00:00.10"
    max_time_diff = 240 # arbitrary initialization, min should be under 4 minutes = 240 s
    epoch_data = get_data()
    ind = 0
    for epoch in epoch_data:
        time_diff_s = time_diff_calc(epoch['EPOCH'], curr_time)
        if abs(time_diff_s) < max_time_diff:
            closest_ind = ind
            max_time_diff = abs(time_diff_s)
        ind +=1
#    return_vectors_speed = epoch_data[closest_ind]
    closest_data = epoch_data[closest_ind]

    vx = float(closest_data["X_DOT"]["#text"])
    vy = float(closest_data["Y_DOT"]["#text"])
    vz = float(closest_data["Z_DOT"]["#text"])
    v = (vx**2 + vy**2 + vz**2) ** 0.5
    return_V_dict = {"instantaneous speed": v, "speed units" : closest_data["X_DOT"]["@units"]}

    geo_data = return_location(closest_data["EPOCH"])

    return_V_dict.update(geo_data)
    return_V_dict.update({"position units": "km"})
    return return_V_dict


def time_diff_calc(other_time:str, now_time:str)->float:
    """
    Function calculates the time difference between two strings representing different dates (different format). 
    Args:
        other_time (str) : a UTC timepoint, i.e "2024-053T00:00:00.000Z"
        now_time (str) : the current UTC time, i.e "2024-02-22 00:00:00.692649"
    Returns:
        total_seconds (float): the total seconds between the now_time and other_time.
    """
    timestamp1 = datetime.strptime(other_time, "%Y-%jT%H:%M:%S.%fZ")
    timestamp2 = datetime.strptime(now_time, "%Y-%m-%d %H:%M:%S.%f")
    time_difference = timestamp2 - timestamp1
    total_seconds = time_difference.total_seconds()
    return total_seconds

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
