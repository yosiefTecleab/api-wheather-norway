import streamlit as st
import requests
from datetime import datetime
import json

CLIENT_ID = '83ff59d0-b168-4e05-88af-70d2412d2799'


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

  place_string = st.text_input('Skriv byen du vil finne temperatur for')

  date_string = st.date_input('Skriv datoen du vil finne temperatur for:',
                              format="DD.MM.YYYY",
                              value=None)

  if st.button('hent Værdata'):
    station_found = get_source_id(place_string)
    if len(station_found) != 0 and date_string:

      DATE = date_string
      SOURCE_ID = station_found[0]

      
      #print(datetime.now().strftime('%d.%m.%Y'))

      #print(f'Temperatur for Oslo {DATE} ')
      st.write(f"Temperatur for {place_string} {date_string} {SOURCE_ID} ")

      for HOUR in range(24):
        HOUR_STR = str(HOUR).zfill(2)  # Pad single digits with leading zero
        REFERENCE_TIME = f"{DATE}T{HOUR_STR}:00:00Z"
        URL = f"https://frost.met.no/observations/v0.jsonld?sources={SOURCE_ID}&referencetime={REFERENCE_TIME}&elements=air_temperature"
        response = requests.get(URL, auth=(CLIENT_ID, ''))
        data = response.json()

        hour = data['data'][0]['referenceTime']
        hourly_temperature = data['data'][0]['observations'][0]['value']

        #extract hour in 4 digit format
        hour_4digits = hour[hour.index('T') + 1:hour.index('T') + 6]

        #e.g  Kl 00:00 10 grader
        output = f'Kl {hour_4digits} {hourly_temperature} grader'

        #print(output)
        st.write(output)

    else:
      st.write('Ikke funnet')


if __name__ == "__main__":
  main()