import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import ast

# animate avalanche data
df = pd.read_csv(r'C:\Users\derek\Documents\Coding Practice\avy-predictions\avy_data')

# get test data and clean up string
test_data = df.iloc[1,1]
test_data = ast.literal_eval(test_data)

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
    4 : (0, 0, 0)
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

print(f'radii {radii}')
print(f'theta {theta}')
print(f'colors {colors}')

tick_labels = ["E", "NE", "N", "NW", "W", "SW", "S", "SE"]
tick_labels = tick_labels + tick_labels + tick_labels

# create the plot
ax = plt.subplot(projection='polar')
ax.bar(theta, radii, width=width, bottom=bottom, color=colors, alpha=1, edgecolor='black', tick_label = tick_labels)
ax.set_rlabel_position(145)
plt.grid(False)
plt.yticks(ticks=[3.5, 7.5, 12], labels=['H', 'M', 'L'], bbox=dict(boxstyle='round,pad=0.3', edgecolor='black', facecolor='lightgray'), rotation=180)

# add title date
# add legend that shows elevation
# convert into an a function
# create a parallel animation function

plt.show()