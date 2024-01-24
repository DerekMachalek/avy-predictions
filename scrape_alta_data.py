from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
import helium
import time

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

    # sort by date/time
    print(snow_df.sort_values('Date/Time (L)'))

    return snow_df

# scrape data frame
test_df = historical_alta_snow(2024, 1, 6, 5, 24)

# save to csv
test_df.to_csv(r'C:\Users\derek\Documents\Coding Practice\avy-predictions\avy-data1', index = False)

# load from csv

# print out data
print(test_df)

#adjust dates and select values in specified range