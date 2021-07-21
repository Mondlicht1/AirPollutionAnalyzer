"""
CSC110 Course Project: Air Pollution and Forestry
===================================================================================
data_extract.py

Provides functions to convert data from differnt official data sources to the format
that can be used by the simulator. This format is described in the report.
====================================================================================
@author: Tu Anh Pham
"""
import csv
from typing import Dict, List, Set
import json


WORLD_GEO = {}


##############################################################
#              File format converting functions              #
##############################################################
# Helps converting various types of csv, tsv formatting to the
# csv formatting required by the data manager. This data format
# is described in the report.
def world_bank_data_convert(filepath: str) -> None:
    """Create a new file from the original data set obtained from the world bank that only
    contains the important rows and columns.
    The new data file follows the format required by the simulator.
    """

    new_filepath = filepath[0:-4] + '_formatted.csv'
    with open(filepath) as fp_in, open(new_filepath, 'w', newline='') as fp_out:
        reader = csv.reader(fp_in)
        writer = csv.writer(fp_out, delimiter=",")
        # Skip the first 4 rows
        for _ in range(4):
            next(reader)

        for row in reader:
            # Delete the unnecessary columns with no data
            del row[2:34]
            writer.writerow(row)


def anime_reviews_data_convert(filepath: str) -> None:
    """Create a new file from the original data set obtained from Kaggle.
    The new data file follows the format required by the recommendation engine.
    """

    new_filepath = filepath[0:-4] + '_formatted.csv'
    with open(filepath) as fp_in, open(new_filepath, 'w', newline='') as fp_out:
        reader = csv.reader(fp_in)
        writer = csv.writer(fp_out, delimiter=",")
        # Skip the first 4 rows
        for _ in range(4):
            next(reader)

        for row in reader:
            # Delete the unnecessary columns with no data
            del row[2:34]
            writer.writerow(row)


def motor_vehicle_file_merge(wb_file: str, nm_file: str) -> None:
    """Merge the motor vehicle per 1000 inhabitants data from world bank file with a data
    file from National Master to produce a new file.
    The new data file follows the format required by the simulator.
    The new file will be named 'motor_vehicle_formatted.csv', stored in the 'Data' folder.

        - wb_file: the file path to the csv file formatted by the World Bank.
        - nm_file: the filepath to the csv file formatter by National Master.
    """

    vehicle_2014 = read_national_master_data(nm_file)
    formatted_vehicle = 'Data/motor_vehicle_formatted.csv'
    with open(wb_file) as fp_in, open(formatted_vehicle, 'w', newline='') as fp_out:
        reader = csv.reader(fp_in)
        writer = csv.writer(fp_out, delimiter=",")

        # Skip the first two rows
        next(reader)
        next(reader)

        header = next(reader)
        # Delete the unnecessary columns with no data
        del header[2:33]
        header.append('2014')
        writer.writerow(header)

        for row in reader:
            row.append("")  # adding a "place holder" for 2014 data
            country_code = row[1]
            # Adding the 2014 data
            if country_code in vehicle_2014:
                row[-1] = vehicle_2014[country_code]

            del row[2:33]
            writer.writerow(row)


def vertical_year_data_convert(filepath: str, iso3_col: int,
                               year_col: int, value_col: int) -> None:
    """Create a new file from the original data sets that has years in a column
    The new data file follows the format required by the simulator.
        - iso3_column = 0, 1, 2... is the index of the column contain country codes
        - year_column = 0, 1, 2,... is the index of the column containing the year
        - value_column = 0, 1, 2,... is the index of the column containing the data value.

    Preconditions:
        - iso_col, year_col, and value_col match the column indices in the provided
        data file.
    """
    code_to_name = get_country_code_to_name()

    new_filepath = filepath[0:-4] + '_formatted.csv'
    with open(filepath) as fp_in, open(new_filepath, 'w', newline='') as fp_out:
        reader = csv.reader(fp_in)
        writer = csv.writer(fp_out, delimiter=",")
        # Skip the header
        next(reader)

        new_header = ['Country Name', 'Country Code'] + [str(year) for year in range(1990, 2020)]
        writer.writerow(new_header)
        # Accumulator: a dictionary mapping country code to their corresponding row in the correct
        # format.
        country_data = {}

        for row in reader:
            if row[iso3_col] not in country_data and row[iso3_col] in code_to_name:
                # Initialize a list (data row) with empty strings as placeholders.
                country_data[row[iso3_col]] = [code_to_name[row[iso3_col]], row[iso3_col]] + \
                                              ["" for _ in range(1990, 2020)]
            if row[iso3_col] in code_to_name and int(row[year_col]) in range(1990, 2020):
                # row[5] is the year and row[6] is the data
                country_data[row[iso3_col]][int(row[year_col]) - 1988] = row[value_col]

        for row in sorted(country_data.values(), key=lambda lst: lst[0]):
            writer.writerow(row)


def acag_data_combine() -> None:
    """Combine the data files of air pollution from the atmospheric composition analysis group
    from year 1998 to 2018"""
    # Accumulator: a dictionary mapping country code to their corresponding row in the correct
    # format.
    with open('Data/air_pollution_formatted.csv', 'w', newline='') as fp_out:
        writer = csv.writer(fp_out, delimiter=",")
        new_header = ['Country Name', 'Country Code'] + [str(year) for year in range(1990, 2020)]
        writer.writerow(new_header)
        country_data = {}
        for year in range(1998, 2019):
            add_acag_data(country_data, year)

        for row in sorted(country_data.values(), key=lambda lst: lst[0]):
            writer.writerow(row)


# Helper
def add_acag_data(country_data: dict, year: int) -> None:
    """Mutate the country_data dictionary, add the air pollution data of a
    year to it."""
    filepath = 'Data/' + str(year) + '.csv'
    with open(filepath) as file_in:
        reader = csv.reader(file_in)
        next(reader)
        code_to_name = get_country_code_to_name()
        for row in reader:
            if row[0] not in country_data and row[0] in code_to_name:
                country_data[row[0]] = [code_to_name[row[0]], row[0]] + \
                                              ["" for _ in range(1990, 2020)]
            if row[0] in code_to_name:
                country_data[row[0]][year - 1988] = row[2]


def undp_data_convert(filepath: str) -> None:
    """Create a new file from the original data set obtained from the united nation
    development program that only contains the important rows and columns.

    The new data file follows the format required by the simulator.
    """
    new_filepath = filepath[0:-4] + '_formatted.csv'
    with open(filepath) as fp_in, open(new_filepath, 'w', newline='') as fp_out:
        reader = csv.reader(fp_in)
        writer = csv.writer(fp_out, delimiter=",")
        # Skip the first 2 rows
        next(reader)
        next(reader)
        # extracting the years + reformatting the header.
        header = ['Country Name', 'Country Code'] + [str(year) for year in range(1990, 2019)]
        writer.writerow(header)

        name_to_code = get_country_name_to_code()
        for row in reader:
            if row[1] in name_to_code:
                # Extract the data from 1990 to 2018
                # and remove the blank columns that separate entries in to original file.
                new_row = [row[1], name_to_code[row[1]]] + [row[i * 2] for i in range(1, 30)]
                writer.writerow(new_row)


def neci_tsv_data_convert(filepath: str) -> None:
    """Create a new file from the original data set obtained from the national centers for
    environmental information that only contains the important rows and columns.

    The new data file follows the format required by the simulator.
    """
    new_filepath = filepath[0:-4] + '_formatted.csv'
    with open(filepath) as fp_in, open(new_filepath, 'w', newline='') as fp_out:
        reader = csv.reader(fp_in, delimiter="\t")
        writer = csv.writer(fp_out, delimiter=",")
        # Skip the first 2 rows
        next(reader)
        next(reader)
        # Creating a new header that match the required format
        header = ['Country Name', 'Country Code'] + [str(y) for y in range(1990, 2021)]
        writer.writerow(header)

        name_to_code = get_country_name_to_code()
        # Accumulator: The dictionary mapping country names to dictionaries of years to volcanic
        # eruption counts
        country_to_data = {}
        for row in reader:
            if row[8] in name_to_code:  # row[8] is the country name.
                if row[8] not in country_to_data:
                    # Create an accumulator: a mapping of year to eruption counts
                    country_to_data[row[8]] = {year: 0 for year in range(1990, 2021)}
                country_to_data[row[8]][int(row[1])] += 1   # row[1] is the year

        # Write data to the new file:
        for name in country_to_data:
            data_by_year = [str(country_to_data[name][year]) for year in range(1990, 2021)]
            new_row = [name, name_to_code[name]] + data_by_year
            writer.writerow(new_row)


def open_ei_data_convert(filepath: str) -> None:
    """Create a new file from the original data set obtained from openei.org that only
    contains the important rows and columns.
    The new data file follows the format required by the simulator.
    """

    new_filepath = filepath[0:-4] + '_formatted.csv'
    with open(filepath) as fp_in, open(new_filepath, 'w', newline='') as fp_out:
        reader = csv.reader(fp_in)
        writer = csv.writer(fp_out, delimiter=",")

        header = next(reader)
        header[0] = 'Country Name'
        header.insert(1, 'Country Code')
        writer.writerow(header)

        name_to_code = get_country_name_to_code()
        for row in reader:
            if row[0] in name_to_code:
                row.insert(1, name_to_code[row[0]])
                writer.writerow(row)


def iea_data_convert(filepath: str) -> None:
    """Create a new file from the original data set obtained from iea that only
    contains the important rows and columns.
    The new data file follows the format required by the simulator.
    """

    new_filepath = filepath[0:-4] + '_formatted.csv'
    with open(filepath) as fp_in, open(new_filepath, 'w', newline='') as fp_out:
        reader = csv.reader(fp_in)
        writer = csv.writer(fp_out, delimiter=",")

        for _ in range(3):
            # Skip the first 3 rows
            next(reader)

        header = next(reader)
        new_header = ['Country Name', 'Country Code'] + [str(y) for y in range(1990, 2021)]
        writer.writerow(new_header)

        name_to_code = get_country_name_to_code()
        # Accumulator: The dictionary mapping country names to list of data values from 1990 to 2020
        country_to_data = {}
        for row in reader:
            year = int(row[0])
            # Extract the data from 1990 to 2020
            if year in range(1990, 2021):
                add_iea_data_year(year, row, header, name_to_code, country_to_data)

        # Write data to the new file:
        for name in country_to_data:
            new_row = [name, name_to_code[name]] + country_to_data[name]
            writer.writerow(new_row)


#########################################################
#           File reading and helper functions           #
#########################################################
# These function serves the data manager as well as the
# above file converting functions.

def create_world_geo_from_json(filepath: str) -> Dict[str, Dict[str, str]]:
    """Returns a mapping of alpha-3 country codes to their corresponding geographical information,
    which is also a mapping that includes the following keys:
        - 'name'
        - 'region'
        - 'sub-region'
        - 'int-region'
    """
    with open(filepath) as json_file:
        data = json.load(json_file)

        # Accumulator: The mapping of country codes to country information.
        countries_so_far = {}
        for country in data:
            countries_so_far[country['alpha-3']] = {'name': country['name'],
                                                    'region': country['region'],
                                                    'sub-region': country['sub-region'],
                                                    'int-region': country['intermediate-region']}

    return countries_so_far


def create_region_group_data() -> Dict[str, Dict[str, Set[str]]]:
    """Returns a mapping of region types (e.g. 'region', 'sub-region', 'int-region') to the
    dictionaries of regions in those region types to sets of country alpha-3 codes.
    e.g: {'region': {'Asia': {JPN, CHN}}, 'sub-region': {}, 'int-region': {}}
    """
    world_map = create_world_geo_from_json('Data/country_by_region.json')

    # Accumulator: The mapping of region types to region dictionaries.
    regions_so_far = {'region': {}, 'sub-region': {}, 'int-region': {}}

    for country_code in world_map:
        country_reg = world_map[country_code]['region']
        country_sub_reg = world_map[country_code]['sub-region']
        country_int_reg = world_map[country_code]['int-region']

        if country_reg not in regions_so_far['region']:
            regions_so_far['region'][country_reg] = set()
        if country_sub_reg not in regions_so_far['sub-region']:
            regions_so_far['sub-region'][country_sub_reg] = set()
        if country_int_reg not in regions_so_far['int-region']:
            regions_so_far['int-region'][country_int_reg] = set()

        set.add(regions_so_far['region'][country_reg], country_code)
        set.add(regions_so_far['sub-region'][country_sub_reg], country_code)
        set.add(regions_so_far['int-region'][country_int_reg], country_code)

    return regions_so_far


def read_formatted_row(row: List[str], header: List[str]) -> Dict[int, float]:
    """Returns a dictionary mapping year to data value in a row, which correspond to a country.

    Preconditions:
        - row follows the format described in the report.
    """
    # Accumulator: The mapping each year to forest area in that year
    row_data = {}

    for i in range(2, len(row)):
        try:
            year = int(header[i])
            row_data[year] = float(row[i])
        except ValueError:
            continue    # not adding the invalid value to row_data and keep looping

    return row_data


def read_national_master_data(filepath: str) -> Dict[str, str]:
    """Reads the csv file from National Master.
    Returns a mapping of country code to the number of motor vehicles per
    1000 inhabitants in year 2014 (the numbers are in str form: "<float_value>").
    """
    # Table of country name to code to look up
    name_to_code = get_country_name_to_code()
    # Accumulator: The mapping of country code to number of motor vehicle /1000 people
    # in 2014 only.
    vehicle_data = {}
    with open(filepath) as file:
        reader = csv.reader(file)
        # skip the header
        next(reader)

        for row in reader:
            if row[0] in name_to_code:
                code = name_to_code[row[0]]
                vehicle_data[code] = str(float(row[1].replace(',', '')))

    return vehicle_data


def add_iea_data_year(year: int, row: List[str], header: List[str],
                      name_to_code: Dict[str, str],
                      country_to_data: Dict[str, List[str]]) -> None:
    """Mutate the country_to_data dictionary, adding new annual data correspond to the
    given year."""
    for i in range(1, len(row)):
        if header[i] in name_to_code:
            if header[i] not in country_to_data:
                # initialize a list of empty strings as place holder for the actual
                # values, if present
                country_to_data[header[i]] = ["" for _ in range(1990, 2021)]
            country_to_data[header[i]][year - 1990] = row[i]


def get_country_code_to_name() -> Dict[str, str]:
    """Returns a dictionary mapping country codes to country names.

    Preconditions:
        - world_geo is not None
    """
    global WORLD_GEO
    # Accumulator: The mapping of country code to country name
    code_to_name = {}

    for code in WORLD_GEO:
        code_to_name[code] = WORLD_GEO[code]['name']

    return code_to_name


def get_country_name_to_code() -> Dict[str, str]:
    """Returns a dictionary mapping country names to country codes.

    Preconditions:
        - world_geo is not None
    """
    global WORLD_GEO
    # Accumulator: The mapping of country name to country code
    name_to_code = {}

    for code in WORLD_GEO:
        name_to_code[WORLD_GEO[code]['name']] = code

    return name_to_code


if __name__ == '__main__':
    WORLD_GEO = create_world_geo_from_json('Data/country_by_region.json')
    import python_ta

    python_ta.check_all(config={'max-line-length': 100})
