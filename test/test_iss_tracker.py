
from ISSTracker.iss_tracker import time_diff_calc # does not have flask acess
import importlib
from datetime import datetime, timedelta
import requests
import json
import xmltodict

LARGE_MACHINE_PRECISION = .01
SMALL_MACHINE_PRECISION = .000

def request_data(url:str):
    response = requests.get(url)
    response_content_str = response.content.decode('utf-8')  # Convert bytes to string
    cleaned_dictionary = json.loads(response_content_str.replace('\n', ''))
    return cleaned_dictionary

def test_get_data():
    cleaned_dictionary = request_data("http://127.0.0.1:5000/epochs")
    should_have_keys = ['EPOCH', 'X', 'X_DOT', 'Y', 'Y_DOT', 'Z', 'Z_DOT']
    assert(list(cleaned_dictionary[0].keys()) == should_have_keys)

def test_return_comments():
    cleaned_dictionary = request_data("http://127.0.0.1:5000/comment")
    assert(cleaned_dictionary[0] == "Units are in kg and m^2")
    assert(cleaned_dictionary[-1] == "End sequence of events")
    assert(isinstance(cleaned_dictionary, list))

def test_return_header():
    cleaned_dictionary = request_data("http://127.0.0.1:5000/header")
    assert(isinstance(cleaned_dictionary, dict))
    keyval = list(cleaned_dictionary.keys())
    assert("CREATION_DATE" in keyval)
    assert("ORIGINATOR" in keyval)
    assert("JSC" == cleaned_dictionary["ORIGINATOR"])
    now_vs_creation = time_diff_calc(cleaned_dictionary["CREATION_DATE"], str(datetime.utcnow()))
    assert (now_vs_creation > 0 ) # time_diff_calc  takes 2nd minus 1st time; now is after origination (positive time delta)
    

def test_return_meta_data():
    cleaned_dictionary = request_data("http://127.0.0.1:5000/metadata")
    assert(isinstance(cleaned_dictionary, dict))
    assert(cleaned_dictionary["OBJECT_NAME"] == "ISS")
    assert(cleaned_dictionary["OBJECT_ID"] == "1998-067-A")
    assert(cleaned_dictionary["CENTER_NAME"] == "EARTH")
    assert(cleaned_dictionary["REF_FRAME"] == "EME2000")
    assert(cleaned_dictionary["TIME_SYSTEM"]=="UTC")
    assert(cleaned_dictionary["START_TIME"][-13:] == "12:00:00.000Z")
    assert(cleaned_dictionary["STOP_TIME"][-13:] == "12:00:00.000Z")
    start_day = cleaned_dictionary["START_TIME"][-16:-14]
    stop_day = cleaned_dictionary["STOP_TIME"][-16:-14]
    assert(int(stop_day)-int(start_day) == 15) # 15 days of data collection
#    assert(start_day ==50)
def test_return_entire_dataset():
    cleaned_dictionary = request_data('http://127.0.0.1:5000/epochs')
    response = requests.get("https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS\
.OEM_J2K_EPH.xml")
    data_dict = xmltodict.parse(response.content)
    edata = data_dict['ndm']['oem']['body']['segment']['data']['stateVector']
    le = len(cleaned_dictionary)
    assert(le == len(edata))

    should_have_keys = ['EPOCH', 'X', 'X_DOT', 'Y', 'Y_DOT', 'Z', 'Z_DOT']
    assert(list(cleaned_dictionary[0].keys()) == should_have_keys)
    
    cleaned_dictionary = request_data('http://127.0.0.1:5000/epochs?limit=2')
    assert(len(cleaned_dictionary)==2)

    cleaned_dictionary = request_data(f'http://127.0.0.1:5000/epochs?offset={le-1}')
    assert(len(cleaned_dictionary)==1)

    cleaned_dictionary = request_data(f"http://127.0.0.1:5000/epochs?limit=3&offset={le}")
    assert(len(cleaned_dictionary)==0) # no entries returned, since offset is already at end


def test_specific_epoch_data_and_instspeed():

    cleaned_dictionary = request_data('http://127.0.0.1:5000/epochs')
    an_epoch = cleaned_dictionary[100]["EPOCH"]

    cleaned_dictionary = request_data(f'http://127.0.0.1:5000/epochs/{an_epoch}')
    should_have_keys = ['EPOCH', 'X', 'X_DOT', 'Y', 'Y_DOT', 'Z', 'Z_DOT']
    assert(list(cleaned_dictionary.keys()) == should_have_keys)

    for key, value in cleaned_dictionary.items():
        if key != "EPOCH":
            try:
                # Extract the value from the "#text" field and convert it to a float
                float_value = float(value["#text"])
                assert isinstance(float_value, float), f"Value for key '{key}' is not a float."
            except (KeyError, ValueError):
                raise AssertionError(f"Invalid value for key '{key}': {value}")


    cleaned_dictionary = request_data(f'http://127.0.0.1:5000/epochs/{an_epoch}/speed')
    keys_equal = ['instantaneous speed', 'speed units']
    assert(list(cleaned_dictionary.keys()) == keys_equal)

    units_equal = 'km/s'
    assert(cleaned_dictionary["speed units"] == units_equal)

    assert(cleaned_dictionary["instantaneous speed"] >= 0)



def test_return_location():
    cleaned_dictionary = request_data('http://127.0.0.1:5000/epochs')
    an_epoch = cleaned_dictionary[100]["EPOCH"]


    cleaned_dictionary = request_data(f'http://127.0.0.1:5000/epochs/{an_epoch}/location')

    should_have_keys = ['geodata', 'iss_position','timestamp']
    assert(list(cleaned_dictionary.keys()) == should_have_keys)

    assert(list(cleaned_dictionary["iss_position"].keys()) == ["x", "y", "z"])
    assert(isinstance(cleaned_dictionary["iss_position"]["x"],float))
    assert(isinstance(cleaned_dictionary["iss_position"]["y"],float))
    assert(isinstance(cleaned_dictionary["iss_position"]["z"],float))
    
    assert(list(cleaned_dictionary["geodata"].keys()) == ["altitude", "geolocation/city", "latitude", "longitude"])
    assert(isinstance(cleaned_dictionary["geodata"]["latitude"],float))
    assert(isinstance(cleaned_dictionary["geodata"]["longitude"],float))
    assert(isinstance(cleaned_dictionary["geodata"]["altitude"],float))
    assert(isinstance(cleaned_dictionary["geodata"]["geolocation/city"],str))

    
    assert(isinstance(cleaned_dictionary["timestamp"],str))


def test_closest_epoch():
    keys_equal = ['geodata', 'instantaneous speed', 'iss_position', 'position units', 'speed units', 'timestamp']
    cleaned_dictionary = request_data(f'http://127.0.0.1:5000/now')
    assert(list(cleaned_dictionary.keys()) == keys_equal)

    assert(list(cleaned_dictionary["geodata"].keys())==["altitude","geolocation/city","latitude","longitude"])
    assert(isinstance(cleaned_dictionary["geodata"]["altitude"],float))
    assert(isinstance(cleaned_dictionary["geodata"]["geolocation/city"],str))
    assert(isinstance(cleaned_dictionary["geodata"]["latitude"],float))
    assert(isinstance(cleaned_dictionary["geodata"]["longitude"],float))


    assert(cleaned_dictionary["instantaneous speed"] >= 0)

    assert(list(cleaned_dictionary["iss_position"].keys())==["x","y","z"])
    assert(isinstance(cleaned_dictionary["iss_position"]["x"],float))
    assert(isinstance(cleaned_dictionary["iss_position"]["y"],float))
    assert(isinstance(cleaned_dictionary["iss_position"]["z"],float))
    
    pos_units_equal = 'km'
    speed_units_equal = "km/s"
    
    assert(cleaned_dictionary["position units"] == pos_units_equal)
    assert(cleaned_dictionary["speed units"] == speed_units_equal)
    assert(isinstance(cleaned_dictionary["timestamp"],str))

    

def test_time_diff_calc():
    other_time = "2024-059T00:00:00.000Z"
    now_time = "2024-02-28 00:00:20.692649"
    assert(abs(time_diff_calc(other_time, now_time)-20.692649) <= SMALL_MACHINE_PRECISION)

test_get_data()




