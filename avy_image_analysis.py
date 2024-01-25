from PIL import Image

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
def pull_avy_severity(image_path):

    # open the image
    im = Image.open(image_path)

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
        (255, 242, 0, 255): 1,
        (247, 148, 30, 255): 2
    }

    # print pixel value
    for i, j in zip(x_vals, y_vals):
        # look up colors in dictionary and replace them
        pixel_color = pix[i, j]
        severityValues.append(color_dict[pixel_color])

    # avy severity from N -> NW clockwise (8 values) for all L elevations and then repeated for M and H.
    return severityValues

print(pull_avy_severity(r'C:\Users\derek\Documents\Coding Practice\avy-predictions\test_avy_image1.png'))
# [2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2]