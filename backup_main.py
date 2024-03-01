import streamlit as st
import requests
from datetime import datetime
import json
import re


st.title("Værdata")
col1, col2, col3, col4 = st.columns([3, 3, 3, 3])  # global s\declares columns


def sources():
  url = "https://frost.met.no/sources/v0.jsonld"
  data = []
  # Send a GET request to the API
  response = requests.get(url, auth=(CLIENT_ID, ''))
  

  # Check if the request was successful (status code 200)
  if response.status_code == 200:
    # Parse JSON response
    data = response.json()

    # Define the file name to save JSON data
    file_name = "source_id.json"

    # Write JSON data to file
    with open(file_name, "w") as file:
      json.dump(data, file)

    print(f"Data saved to {file_name}")
  else:
    print("Failed to fetch data from the API")


def get_source_id(place):
  #place='tron'

  with open("source_id.json", "r") as file:
    id = json.load(file)  #json
    data = id["data"]

  source_id_dict = {}

  #place with the corresponding source id stored in dictionery
  for i in range(len(data)):
    if data[i]['@type'] == 'SensorSystem':
      #if data[i]['country'] == 'Norge':
      source_id_dict[data[i]['name']] = data[i]['id']

  #some cities have more source stations
  stations = []

  for key in source_id_dict:
    place_name = re.split(' -|/', key)[0]
    #for word in key.split(' '):
    if place_name == place.upper():
      stations.append(source_id_dict[key])
  return stations


def calculate_average(data):
  
  return round(sum(data) / len(data), 1) if len(data) > 0 else 0.0



def partition_of_day(temperature_data):
    part1 = temperature_data[0:8]  # 00-08
    part2 = temperature_data[8:12]  # 08-12
    part3 = temperature_data[12:18]  # 12-18
    part4 = temperature_data[18:]  # 18-00

    average_part1 = calculate_average(part1)
    average_part2 = calculate_average(part2)
    average_part3 = calculate_average(part3)
    average_part4 = calculate_average(part4)
    

    #  f'{col1.write(ou+" grader") if NAME== "air_temperature"  else col1.write(ou+ " m/s") }'

    # Print the average temperature for each part
    
    part1=f"00-08: fra {temperature_data[0]} til {temperature_data[7]} grader (snittemperatur {average_part1} grader)"
    col4.write(part1)

    part2=f"08-12: fra {temperature_data[8]} til {temperature_data[11]} grader (snittemperatur {average_part2} grader)"
    col4.write(part2)

    part3=f"12-18: fra {temperature_data[12]} til {temperature_data[17]} grader (snittemperatur {average_part3} grader)"
    col4.write(part3)

    part4=f"18-00: fra {temperature_data[18]} til {temperature_data[23]} grader (snittemperatur {average_part4} grader)"
    col4.write(part4)

    # Overall average temperature

    grand_average = round(sum(temperature_data) / len(temperature_data), 1)
    grand=f"'Daglig snittemperatur:', {round(grand_average, 1)}"
    col4.write(grand)



def fetch_temperature_or_wind(place_string, date_string, NAME):
  #if st.button('hent Værdata'):
  station_found = get_source_id(place_string)
  sum = 0
  hourly_data=[]

  if len(station_found) != 0 and date_string:

    DATE = date_string
    SOURCE_ID = ''
    damaged_source_id = [
        'SN18703', 'SN18165', 'SN18269', 'SN44620', 'SN50539', 'SN44660',
        'SN44580'
    ]
    #col2.write(f"{NAME} for {place_string} {date_string} {SOURCE_ID} ")

    for index in range(len(station_found)):
      if not station_found[index] in damaged_source_id:
        SOURCE_ID = station_found[index]

    #print(datetime.now().strftime('%d.%m.%Y'))

    #print(f'Temperatur for Oslo {DATE} ')
    title = f"{NAME} for {place_string} {date_string} {SOURCE_ID} "
    f'{col2.write(title) if NAME== "air_temperature"  else col3.write(title) }'
    #col2.write(f"{NAME} for {place_string} {date_string} {SOURCE_ID} ")
    output = []
    for HOUR in range(24):
      HOUR_STR = str(HOUR).zfill(2)  # Pad single digits with leading zero
      REFERENCE_TIME = f"{DATE}T{HOUR_STR}:00:00Z"
      URL = f"https://frost.met.no/observations/v0.jsonld?sources={SOURCE_ID}&referencetime={REFERENCE_TIME}&elements={NAME}"

      response = requests.get(URL, auth=(st.secrets["CLIENT_ID"], ''))

      data = response.json()

      hour = data['data'][0]['referenceTime']
      hourly_temperature_or_wind = data['data'][0]['observations'][0]['value']
      hourly_data.append(hourly_temperature_or_wind)
      #print(data['data'])
      sum += hourly_temperature_or_wind

      #extract hour in 4 digit format
      hour_4digits = hour[hour.index('T') + 1:hour.index('T') + 6]

      output.append(
          f'Kl {hour_4digits} {hourly_temperature_or_wind} {"grader" if NAME== "air_temperature"  else "m/s"  }'
      )
      #output.append(f'Kl {hour_4digits} {hourly_temperature_or_wind} grader ')

      #print(output)
    f'{col2.write(output) if NAME== "air_temperature"  else col3.write(output) }'
    #f'{col2.write(output) }'

  else:
    col1.write('Ikke funnet')

  average = round(sum / 24, )
  ou = f'Snitt {NAME} i {place_string} er: {average}'
  f'{col1.write(ou+" grader") if NAME== "air_temperature"  else col1.write(ou+ " m/s") }'
  
  return hourly_data

def main():

  place_string = col1.text_input('Skriv byen du vil finne temperatur for')

  date_string = col1.date_input('Skriv datoen du vil finne temperatur for:',
                                format="DD.MM.YYYY",
                                value=None)

  if col2.button('hent temperature'):
    fetch_temperature_or_wind(place_string, date_string, 'air_temperature')
  if col3.button('hent vind'):
    fetch_temperature_or_wind(place_string, date_string, 'wind_speed')
  if col4.button('daglig deles opp i 4 etapper'):
      partition_of_day(fetch_temperature_or_wind(place_string, date_string, 'air_temperature')
)
      

if __name__ == "__main__":
  #sources()
  main()
