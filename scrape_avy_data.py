from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
import helium
import time
import requests
from PIL import Image 
from io import BytesIO

# helper takes points around the compass rose and moves them towards the center by fraction
def move_points_in(x_vals, y_vals, center, fraction):
    new_x = []
    new_y = []

    for i, j in zip(x_vals, y_vals):
        # calcualte direction to center
        x_direction = center[0] - i
        y_direction = center[1] - j

        # add vector to center to starting point and append
        new_x.append(int(i + x_direction*fraction))
        new_y.append(int(j + y_direction*fraction))

    return new_x, new_y

# pull avalanche severity from the color of the compass rose in the image provided by image_path
def pull_avy_severity(im):

    # load the image
    pix = im.load()

    # hard coded center of compass rose
    center = [200, 155]

    # coordinates from N -> NW clockwise for all L elevations and then repeated for M and H
    x_vals = [200, 290, 320, 290, 200, 110, 80, 110]
    y_vals = [60, 90, 170, 250, 290, 250, 170, 90]

    # find vectors to the center
    middle_x, middle_y = move_points_in(x_vals, y_vals, center, 0.33)
    high_x, high_y = move_points_in(x_vals, y_vals, center, 0.7)

    # combine all x and y values
    x_vals = x_vals + middle_x + high_x
    y_vals = y_vals + middle_y + high_y

    # create a list that stores severities
    severityValues = []

    # create color dictionary from color to severity
    color_dict = {
        (80, 184, 72, 255) : 0,
        (255, 242, 0, 255): 1,
        (247, 148, 30, 255): 2,
        (237, 28, 36, 255) : 3,
        (0, 0, 0, 255) : 4
    }

    # print pixel value
    for i, j in zip(x_vals, y_vals):
        # look up colors in dictionary and replace them
        pixel_color = pix[i, j]
        severityValues.append(color_dict[pixel_color])

    # avy severity from N -> NW clockwise (8 values) for all L elevations and then repeated for M and H.
    return severityValues

# write a function that pulls in avy rating from utahavalanchecenter.org
def historical_avy_data(year, month, day):
    """
    historical_avy_data pulls the avalanche rating from the image on the avalanche website

    :param year the year of the record
    :param month the month of the record
    :param day the day of the record

    :return a pandas data frame of the record
    """

    # create url to query
    # example is https://https://utahavalanchecenter.org/forecast/salt-lake/1/1/2024
    requested_string = str(month) + '/' + str(day) + '/' + str(year)
    url = 'https://utahavalanchecenter.org/forecast/salt-lake/' + requested_string

    # download and parse the page
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    #check that the date on the page matches the requested date
    # the website is set to default to the current date if weird numbers are used
    all_span_items =  soup.find_all('span', {'class' : 'nowrap'})
    page_date_item = all_span_items[1].text
    page_datetime_object = datetime.datetime.strptime(page_date_item, '%A, %B %d, %Y')

    # format requested string to date object
    requested_datetime_object = datetime.datetime.strptime(requested_string, '%m/%d/%Y')

    # if the dates are different, return failure
    if page_datetime_object != requested_datetime_object:
        return -1

    # iterate over images to find the compass rose
    for item in soup.find_all('img'): 
        if item['src'].startswith( '/sites/default/files/forecast/' ):
            compass_rose_URL = 'https://utahavalanchecenter.org' + item['src']
            break

    # request the url and stream in data for analysis
    data = requests.get(compass_rose_URL) 
    img = Image.open(BytesIO(data.content))

    severity = pull_avy_severity(img)

    return severity

print(historical_avy_data(2023, 12, 10))
print(historical_avy_data(2023, 6, 10))