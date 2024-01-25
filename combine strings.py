directions = ["N", "NW", "W", "SW", "S", "SE", "E", "NE"]
elevation = ["Low", "Med", "High"]

new_columns = []
for dir in directions:
    for elev in elevation:
        new_columns.append(f'{dir}_{elev}')

print(new_columns)