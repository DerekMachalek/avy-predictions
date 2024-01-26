from bs4 import BeautifulSoup
import pandas as pd
import datetime
import helium
import time
import mysql.connector
import os
from sqlalchemy import create_engine

# write a function that pulls snow data from the alta-collins station on weather.gov
# return 
def historical_alta_snow(start_year, start_month, start_day, start_hour, duration):
    """
    historical_alta_snow pulls temperature and snowfall data for the alta collins stations

    :param start_year the starting year of the weather record
    :param start_month the starting month of the weather record
    :param start_day the starting day of the weather record
    :param start_hour the starting hour of the weather record
    :param duration the length in hours of the weeather record

    :return a pandas data frame of the record
    """

    # create url to query
    # example is https://www.weather.gov/wrh/timeseries?site=CLN&headers=min&obs=raw&hourly=true&pview=full&history=yes&start=20231128&end=20231202
    
    # only the start and end dates matter and we can only control the days
    # therefore we extract 1 day before and after the request and then cut it out based on the data we want
    start_date = datetime.date(start_year, start_month, start_day) - datetime.timedelta(days = 1)
    end_date = datetime.date(start_year, start_month, start_day) + datetime.timedelta(hours = duration + 24)

    # convert date times to strings
    start_date_string = start_date.strftime('%Y%m%d')
    end_date_string = end_date.strftime('%Y%m%d')

    url = 'https://www.weather.gov/wrh/timeseries?site=CLN&headers=min&obs=raw&hourly=true&pview=full&history=yes&start=' + start_date_string + '&end=' + end_date_string

    # get the url request
    # soup does not work because this page is dynamic
    browser = helium.start_chrome(url, headless = True)

    # give the browser some time to render
    time.sleep(1)

    soup = BeautifulSoup(browser.page_source, 'html.parser')

    helium.kill_browser()

    table = soup.find('table')

    titles = table.find_all('th')

    # list comprehension to create new dataframe
    titles_text = [i.text.strip().replace(u'\xa0', u' ') for i in titles]

    # pull out rows (tr) and data (td) to make data frame
    column_data = table.find_all('tr')

    time.sleep(0.5)

    data_to_add = []

    for row in column_data[1:]:
        row_data = row.find_all('td')
        individual_row_data = [data.text.strip() for data in row_data]
        data_to_add.append(individual_row_data)
        
    
    # create pandas data frame
    snow_df = pd.DataFrame(data_to_add, columns = titles_text)

    return snow_df


def create_hourly_alta_data(cursor):

    # delete table if it exists
    cursor.execute("DROP TABLE IF EXISTS avy_alta_hourly")

    # scrape data to pandas dataframe
    snow_df = historical_alta_snow(2023, 10, 1, 5, 2640)

    #set up engine connection for reading and writing to sql engine
    hostname = "localhost"
    username = os.getenv('avy_db_username')
    password = os.getenv('avy_db_password')
    database = "avalanche_analysis"

    # create a new table with this data
    engine = create_engine("mysql://{user}:{pw}@{host}/{db}".format(host=hostname, db=database, user=username, pw=password))

    # create table from SQL
    snow_df.to_sql("avy_alta_hourly", engine, if_exists = 'append')


#create sql connection
db = mysql.connector.connect(
    host = "localhost",
    # use environmental variables so we can push to public GitHub
    user = os.getenv('avy_db_username'),
    passwd = os.getenv('avy_db_password'),
    #select which database we are looking at
    database = "avalanche_analysis"
)

cursor = db.cursor(buffered = True)


# attempt to query from the database of hourly data and delete if it does not exist
try:
    cursor.execute("SELECT * FROM avy_alta_hourly")
except:
    print('there was an exception')
    create_hourly_alta_data(cursor)
    cursor.execute("SELECT * FROM avy_alta_hourly")

# pull values out into pandas dataframe from SQL and remove index
df = pd.read_sql("SELECT * FROM avy_alta_hourly", db)
df = df.drop(columns=['index'])

# only keep 
columns_to_keep = ['Date/Time (L)', 'Temp. (°F)', '1 HourPrecip(in)']
df = df[columns_to_keep]

# update so january has year 2024 and everything else has year 2023
for i in range(len(df)):
    date = df.iloc[i,0]

    if date[:3] == 'Jan':
        Year = 2024
    else:
        Year = 2023

    date = f'{date}, {Year}'

    datetime_object = datetime.datetime.strptime(date, '%b %d, %I:%M %p, %Y')

    df.iloc[i,0] = datetime_object

df = df.sort_values(by='Date/Time (L)')

# find the first encounter of 4 AM
for i in range(len(df)):
    date = df.iloc[i,0]
    if date.hour == 5:
        index_start = i
        break

# find the last encounter of 4 AM
for i in range(len(df)):
    date = df.iloc[len(df) - i - 1,0]
    if date.hour == 4:
        index_end = len(df) - i
        break

#cut new data frame with start and end at 4 AM
df = df.iloc[index_start:index_end, :]

# new data from pandas for consolidation
weather_data =[]

total_hours = 0
total_temp = 0
total_precip = 0

print(df)

for i in range(len(df)):
    # pull out the hour
    date = df.iloc[i,0]
    hour = date.hour

    # handle missing temps
    if df.iloc[i,1] == '':
        temp = 40
    else:
        temp = float(df.iloc[i,1])

    total_hours += 1
    total_temp += temp
    total_precip += float(df.iloc[i,2])

    # if it is 4 AM add to totals and reset
    if hour == 4:

        weather_data.append([date, total_temp/total_hours, total_precip])

        total_hours = 0
        total_temp = 0
        total_precip = 0

#create new pandas dataframe
# put data and columns together in a data frame
daily_df = pd.DataFrame(weather_data, columns=["date", "average temp (F)", "total precip (in)"])

#set up engine connection for reading and writing to sql engine
hostname = "localhost"
username = os.getenv('avy_db_username')
password = os.getenv('avy_db_password')
database = "avalanche_analysis"

# create a new table with this data
engine = create_engine("mysql://{user}:{pw}@{host}/{db}".format(host=hostname, db=database, user=username, pw=password))

# create table from SQL
daily_df.to_sql("avy_alta_daily_data", engine, if_exists = 'append')

