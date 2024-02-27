# api-wheather-norway

visit url

https://api-wheather-norway-app.streamlit.app/

to fetch the temperature of any city(place) in Norway for a given date.

the user get an hourly temperature for the whole day


https://frost.met.no/authentication.html

use client id and client secret to generate access token

then use the token to fetch sources id and save as json



curl -X GET --header 'Accept: application/json' --header 'Authorization: Basic XXXXXXXXXXXXXXXXXXX' 'https://frost.met.no/sources/v0.jsonld' > source_id.json
