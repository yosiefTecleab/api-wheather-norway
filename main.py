import streamlit as st
import requests
from datetime import datetime
import json


auth=(st.secrets(["CLIENT_ID"]), '')

def get_source_id(place):
  #place='tron'

  with open("source_id.json", "r") as file:
    id = json.load(file)  #json
    data = id["data"]

  source_id_dict = {}

  #place with the corresponding source id stored in dictionery
  for i in range(len(data)):
    if data[i]['@type'] == 'SensorSystem':
      if data[i]['country'] == 'Norge':
        source_id_dict[data[i]['name']] = data[i]['id']

  #some cities have more source stations
  stations = []

  for key in source_id_dict:
    for word in key.split(' '):
      if word == place.upper():
        stations.append(source_id_dict[key])
  return stations


def main():
  st.title("Værdata")
  
  col1,col2,col3=st.columns([1,1,1])

  place_string = col1.text_input('Skriv byen du vil finne temperatur for')

  date_string = col1.date_input('Skriv datoen du vil finne temperatur for:',
                              format="DD.MM.YYYY",
                              value=None)

  if col1.button('hent Værdata'):
    station_found = get_source_id(place_string)
    if len(station_found) != 0 and date_string:

      DATE = date_string
      SOURCE_ID = station_found[0]

      
      #print(datetime.now().strftime('%d.%m.%Y'))

      #print(f'Temperatur for Oslo {DATE} ')
      col2.write(f"Temperatur for {place_string} {date_string} {SOURCE_ID} ")
      sum=0
      for HOUR in range(24):
        HOUR_STR = str(HOUR).zfill(2)  # Pad single digits with leading zero
        REFERENCE_TIME = f"{DATE}T{HOUR_STR}:00:00Z"
        URL = f"https://frost.met.no/observations/v0.jsonld?sources={SOURCE_ID}&referencetime={REFERENCE_TIME}&elements=air_temperature"
        response = requests.get(URL, auth=auth)
        data = response.json()

        hour = data['data'][0]['referenceTime']
        hourly_temperature = data['data'][0]['observations'][0]['value']
        sum+=hourly_temperature

        #extract hour in 4 digit format
        hour_4digits = hour[hour.index('T') + 1:hour.index('T') + 6]

        #e.g  Kl 00:00 10 grader
        output = f'Kl {hour_4digits}  {  hourly_temperature} grader'

        #print(output)
        col2.write(output)

    else:
      col1.write('Ikke funnet')

    average=round(sum/24,2)
    col1.write(f'snitt temperatur er: {average}')


if __name__ == "__main__":
  main()
