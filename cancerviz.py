import math
import csv
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors

def print_table(table):
    """
    Echo a nested list to the console
    """
    for row in table:
        print(row)


def read_csv_file(file_name):
    """
    Given a CSV file, read the data into a nested list
    Input: String corresponding to comma-separated  CSV file
    Output: Nested list consisting of the fields in the CSV file
    """
       
    with open(file_name, newline='') as csv_file:       # don't need to explicitly close the file now
        csv_table = []
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            csv_table.append(row)
    return csv_table



def write_csv_file(csv_table, file_name):
    """
    Input: Nested list csv_table and a string file_name
    Action: Write fields in csv_table into a comma-separated CSV file with the name file_name
    """
    
    with open(file_name, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for row in csv_table:
            csv_writer.writerow(row)



# Part 1 - function that creates a dictionary from a table

def make_dict(table, key_col):
    """
    Given a 2D table (list of lists) and a column index key_col,
    return a dictionary whose keys are entries of specified column
    and whose values are lists consisting of the remaining row entries
    """
    new_dict = {}
    for row in table:
        key = row[key_col]
        copy = list(row)
        copy.remove(key)
        new_dict[key] = copy
    return new_dict

def test_make_dict():
    """
    Some tests for make_dict()
    """
    table1 = [[1, 2], [3, 4], [5, 6]]
    print(make_dict(table1, 0))
    print(make_dict(table1, 1))
    table2 = [[1, 2, 3], [2, 4, 6], [3, 6, 9]]
    print(make_dict(table2, 1))
    print(make_dict(table2, 2))
    
# test_make_dict()



# Part 2 - script for merging the CSV files

CANCER_FIPS_COL = 2
CENTER_FIPS_COL = 0

def merge_csv_files(cancer_csv_file, center_csv_file, joined_csv_file):
    """
    Read two specified CSV files as tables
    Join the these tables by shared FIPS codes
    Write the resulting joined table as the specified file
    Analyze for problematic FIPS codes
    """
    # Read in both CSV files
    cancer_table = read_csv_file(cancer_csv_file)
    centers_table = read_csv_file(center_csv_file)
    centers_dict = make_dict(centers_table, CENTER_FIPS_COL)

    # Compute joined table, print warning about cancer-risk FIPS codes that are not in USA map
    joined_table = []
    for idx in cancer_table:
        fips = idx[2]
        if fips in centers_dict:
            joined_table.append(idx + centers_dict[fips])
        else:
            print("Row", idx, "in cancer risk table not present in USA map")

    write_csv_file(joined_table, joined_csv_file)

    # Print warning about FIPS codes in USA map that are missing from cancer risk data
    cancer_codes = [cancer_table[idx][CANCER_FIPS_COL] for idx in range(len(cancer_table))]
    for center_code in centers_dict:
        if center_code not in cancer_codes:
            print("Code", center_code, "not in cancer risk table")
    return

merge_csv_files("cancer_risk_trimmed.csv", "USA_Counties_with_FIPS_and_centers.csv", "cancer_risk_joined.csv")

## Part 3 - Explanation for anomalous FIPS codes

## https://www1.udel.edu/johnmack/frec682/fips_codes.html
##
## Output anamolies for cancer risk data
## Puerto Rico, Virgin Island, Statewide, Nationwide - FIPS codes are all not present on USA map
## One specific county (Clifton Forge, VA - 51560) is also not present in USA map.
## According URL above, Clifton Forge was merged with another VA county prior to 2001
##
## Output anamolies for USA map
## State_Line, separator - FIPS codes are all not present in cancer-risk data
## One specific county (Broomfield County - 08014) is also not present in cancer-risk data
## Accoring to URL above, Broomfield County was created in 2001
##
## Implies cancer risk FIPS codes were defined prior to 2001, the USA map FIPS codes were defined after 2001

USA_SVG_SIZE = [555, 352]
HOUSTON_POS = [302, 280]
ATLANTA_POS = [420, 220]

# Code to compute area of plot point for scatter()
SCATTER_SCALE = math.pi / (200.0 ** 2)

def compute_county_cirle(county_population):
    """
    Given county population as integer,
    Compute area of circle proportional to population for use as option to scatter() in matplotlib
    """
    return  SCATTER_SCALE * int(county_population)

MAX_LOG_RISK = math.log(1.50E-04, 10)    # maximum cancer risk in table
MIN_LOG_RISK = math.log(8.60E-06, 10)    # minimum cancer risk in table

def create_riskmap(colormap):
    """take a colormap from the module matplotlib.cm
    and returns a function that maps a cancer risk to an RGB
    value from the given colormap"""

    risk_norm = matplotlib.colors.Normalize(vmin=MIN_LOG_RISK, vmax=MAX_LOG_RISK)
    color_mapper = mpl.cm.ScalarMappable(norm=risk_norm, cmap=colormap)
    return lambda risk: color_mapper.to_rgba(math.log10(risk))

def draw_cancer_risk_map(joined_csv_file_name, map_name, num_counties = None):
    """
    Inputs:
    Given a csv file, implement a function that takes the name of the joined cancer-risk
    CSV file (from week three) and the name of the USA map and draws a scatter plot with
    scatter points of fixed size and color at the center of the num_counties counties with
    highest cancer risk. Omitting the final optional argument num_counties should default
    to drawing all counties.
    """
    #read csv file
    table = read_csv_file(joined_csv_file_name)

    # Load map image, note that using 'rb'option in open() is critical since png files are binary
    with open(map_name, 'rb') as map_file:  # using 'r' causes Python to crash :(
        map_img = plt.imread(map_file)

    #  Get dimensions of USA map image
    ypixels, xpixels, bands = map_img.shape

    # Optional code to resize plot as fixed size figure -
    # DPI = 50                  # adjust this constant to resize your plot
    # xinch = xpixels / DPI
    # yinch = ypixels / DPI
    # plt.figure(figsize=(xinch,yinch))

    # Plot USA map
    implot = plt.imshow(map_img)

    # create color mapping
    risk_map = create_riskmap(mpl.cm.jet)

    # Plot scatter points
    for row in table[: num_counties]:
        circle = compute_county_cirle(row[3])
        color = risk_map(float(row[4]))
        xval = float(row[5])
        yval = float(row[6])
        plt.scatter(x=xval * xpixels / USA_SVG_SIZE[0], y=yval * ypixels / USA_SVG_SIZE[1],
                    c=color, s=circle, alpha=0.75)

    plt.show()



print(draw_cancer_risk_map('cancer_risk_joined.csv', 'USA_Counties_1000x634.png'), 500)

