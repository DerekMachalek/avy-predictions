import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
from matplotlib.animation import PillowWriter, FuncAnimation
import mysql.connector
import os
import math

def create_avy_plot(index, df):

    # get test data and clean up string
    test_data = df.iloc[index,1:]

    # format string to datetime
    date = df.iloc[index,0]

    # datetime_object = datetime.datetime.strptime(date, '%Y-%m-%d')

    # reformat to string for title
    plot_title = date.strftime("%B %d, %Y")

    # Total slices of pie
    N = 8

    # setting for each slice so it is full
    width = 2 * np.pi / N

    # pre-allocate arrays
    radii = np.zeros(24)
    theta = np.zeros(24)
    bottom = np.zeros(24)
    colors = []

    # converts severity back to color
    reverse_color_dict = {
        0 : (80/255, 184/255, 72/255),
        1 : (255/255, 242/255, 0),
        2 : (247/255, 148/255, 30/255),
        3 : (237/255, 28/255, 36/255),
        4 : (30/255, 30/255, 30/255)
    }

    def get_polar_values(radius, N, index, colors, radii, theta, bottom, test_data):

        # pull out slice to use for all
        cut_slice = slice(index*N, (index+1)*N) 

        # update colors, bottom and theta
        radii[cut_slice] = 5 * np.ones(N)
        bottom[cut_slice] = (radius-5) * np.ones(N)

        # rotate around entire circle
        theta[cut_slice] = np.linspace(0.0, 2 * np.pi, N, endpoint=False)

        # convert severity to colors
        for severity in test_data[cut_slice]:
            colors.append(reverse_color_dict[severity])

        return -1

    # list of radii from outside to inside, order matters since colors are stacked
    radii_list = [15, 10, 5]

    for count, rad in enumerate(radii_list):
        # np arrays are passed by reference so they are automatically updated
        get_polar_values(rad, N, count, colors, radii, theta, bottom, test_data)

    tick_labels = ["E", "NE", "N", "NW", "W", "SW", "S", "SE"]
    tick_labels = tick_labels + tick_labels + tick_labels

    # create the plot
    ax = plt.subplot(projection='polar')
    ax.bar(theta, radii, width=width, bottom=bottom, color=colors, alpha=1, edgecolor='black', tick_label = tick_labels)
    ax.set_rlabel_position(145)
    plt.grid(False)
    plt.yticks(ticks=[3.5, 7.5, 12], labels=['H', 'M', 'L'], bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='lightgray'), rotation=180)

    # in polar coordinates
    plt.text(np.pi/1.7, 19.8, "this is a string that will cover up the old title", bbox=dict(boxstyle='round,pad=0.3', edgecolor='white', facecolor='white'), fontdict={'size': 14}, color = 'white')
    plt.text(np.pi/1.7, 19.8, plot_title, bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='lightgray'))
    plt.text(np.pi/1.12, 26.5, "H - Above 9,500 ft. \nM - 8,000-9,500 ft. \nL - Below 8,000 ft.", bbox=dict(boxstyle='round', pad=0.3, edgecolor='black', facecolor='lightgray'))

    def cartesian_to_polar(x, y):
        r = math.sqrt(x**2 + y**2)
        theta = math.atan2(y, x)
        return r, theta
    
    r, theta = cartesian_to_polar(-25, -10)
    plt.text(theta, r, "Considerable \nConsiderable \nConsiderable \nConsiderable \nConsiderable", color = 'lightgray', bbox=dict(boxstyle='round', pad=0.3, edgecolor='black', facecolor='lightgray'))
    
    colors = ['black','green', 'yellow', 'orange', 'red', 'black']
    texts = ["Risk", "Low", "Moderate", "Considerable", "High", "Extreme"]
    ycoords = np.linspace(-3, -10, 6)

    for i in range(len(colors)):
        # solve for x,y coordinates from polar
        r, theta = cartesian_to_polar(-25, ycoords[i])
        plt.text(theta, r, texts[i], color = colors[i])

    return plt



#create sql connection
db = mysql.connector.connect(
    host = "localhost",
    # use environmental variables so we can push to public GitHub
    user = os.getenv('avy_db_username'),
    passwd = os.getenv('avy_db_password'),
    #select which database we are looking at
    database = "avalanche_analysis"
)


# pull values out into pandas dataframe from SQL and remove index
df = pd.read_sql("SELECT * FROM avy_risk", db)
df = df.drop(columns=['index'])

fig = plt.figure(figsize = (6.5,5))

anim = FuncAnimation(fig, create_avy_plot, len(df), fargs=(df,), interval = 200)

# saving to m4 using ffmpeg writer 
anim.save("TLI.gif", dpi=100, writer=PillowWriter(fps=4))
