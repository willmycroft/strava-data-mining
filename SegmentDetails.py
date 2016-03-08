# -*- coding: utf-8 -*-

from stravalib.client import Client
from datetime import datetime, timedelta
import csv
import re

# Run this code to get an access token
# client_id = <CLIENT ID>
# secret = "<SECRET>"
# client = Client()
# authorize_url = client.authorization_url(client_id=client_id, redirect_uri='http://localhost:8282/authorized')
# code = "<RETURNED CODE>"
# access_token = client.exchange_code_for_token(client_id=client_id, client_secret=secret, code=code)

if __name__ == "__main__":
    
    segment_id = 8516849 # 2015 Leeds Abbey Dash
    race_time = datetime(2015,11,15)
    output_file = 'data/leeds.times.csv'
    access_token = "<ACCESS TOKEN>"
    client = Client()
    client.access_token = access_token
    
    # Get all efforts on the day of the race
    efforts = client.get_segment_efforts(segment_id,
                                         start_date_local=race_time,
                                         end_date_local=race_time+timedelta(1))   
    
    data = []
    data.append(["athlete_id", "sex", "first_name", "last_name", "time"])  
    print "a"
    counter = 0
    for effort in efforts:
        print counter
        counter = counter + 1
        time = effort.elapsed_time.seconds
        athlete_id = effort.athlete.id   
        athlete = client.get_athlete(athlete_id)
        first_name = re.sub('[^0-9a-zA-Z]+', '', athlete.firstname)
        last_name = re.sub('[^0-9a-zA-Z]+', '', athlete.lastname)
        data.append([athlete_id, athlete.sex, first_name, last_name, time])

    # Write to file
    with open(output_file, 'wb') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(data)                    