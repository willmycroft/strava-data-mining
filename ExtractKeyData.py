# -*- coding: utf-8 -*-

#==============================================================================
# This script extracts the relevant statistics we are interested in
# and compiles them into a single csv file for ease of analysis.
#==============================================================================

from datetime import datetime, timedelta
import csv
import json

##
# An inefficient function to compute the average mileage
# for a time period before the race.
# weekly_mileage - A list of (date strings, mileage) tuples
# date - The date of the race
# weeks - A list of the number of weeks prior to the race we want an average for  
def get_average_mileage(weekly_mileage, date, weeks=[4]):
    averages = []
    for num_weeks in weeks:
        average = 0
        for wb, miles in weekly_mileage:
            if date-timedelta(7*num_weeks) < wb and wb < date: 
                average = average + miles
        average = average*1.0/num_weeks
        averages.append(average)
    return averages
    

if __name__ == "__main__":
    datetime.strptime("2015-01-03", "%Y-%m-%d")
    race_date = datetime(2015,11,15)
    weekly_averages = [1,4,6,8,12,16,26]
    segment_file = "data/leeds.times.csv"
    mileage_file = "data/leeds.mileage.json"
    output_file =  "data/leeds.cleaned.csv"
    
    
    with open(segment_file, 'rb') as segment_file, open(mileage_file, 'rb') as mileage_file:
        
        segment_reader = csv.reader(segment_file)
        segment_reader.next()
        
        mileage_data = json.loads(mileage_file.read())
        
        # Convert date strings into date objects
        for row in mileage_data:
            for mileage in row['mileage']:
                mileage[0] = datetime.strptime(mileage[0], "%Y-%m-%d")
        
        output = []
        header = ["id", "name", "sex", "time", "at_run", "at_cycle"]
        header.extend(map(lambda x: str(x)+"_week_avg", weekly_averages))
        output.append(header)
        for s_row in segment_reader:
            athlete_id = int(s_row[0])
            sex = s_row[1]
            name = s_row[2] + " " + s_row[3]
            time = int(s_row[4])
            
            # Inefficient implementation of a SQL join:
            averages = None
            for m_row in mileage_data:
                if athlete_id == m_row['id']:
                    averages = get_average_mileage(m_row['mileage'], race_date, weekly_averages)
                    at_run = m_row['at_run']
                    at_cycle = m_row['at_cycle']
                    break
            
            if averages is not None:
                o_row = [athlete_id, name, sex, time, at_run, at_cycle]
                o_row.extend(averages)
                output.append(o_row)
                
                
    # Write to file
    with open(output_file, 'wb') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(output)  
        