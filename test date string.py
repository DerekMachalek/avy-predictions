import pandas as pd
import matplotlib.pyplot as plt
import datetime

# animate avalanche data
df = pd.read_csv(r'C:\Users\derek\Documents\Coding Practice\avy-predictions\avy_data')

# get test data and clean up string
test_data = df.iloc[1,1:]
date = df.iloc[1,0]

# format string to datetime
datetime_object = datetime.datetime.strptime(date, '%Y-%m-%d')

print(datetime_object)

print(datetime_object.strftime("%B %d, %Y"))