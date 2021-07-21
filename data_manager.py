"""
CSC110 Course Project: Air Pollution and Forestry
=========================================================================================
DataManager Class
The data manager is responsible for loading, storing, and providing data for other parts.
=========================================================================================
@author: Tu Pham
"""
import csv
from typing import Dict, Set, Optional, List, Tuple, Any

import data_extract
from country import Country


class DataManager:
    """The data manager class, responsible for storing, manipulating, and presenting data.

    """
    # Private Instance Attributes:
    #   - _countries: the mapping of country codes to Country objects.
    #   - regional_groups, a mapping of types of region (e.g. 'region', 'sub-region'..) to
    #   dictionaries of region names and set of country codes.
    #   e.g: _regional_groups = {'region': {'Asia': {JPN, CHN}}, 'sub-region': {}, 'int-region': {}}
    #   - _indicators: The set of all indicators of the data the simulator is currently possess.

    # Private Representation Invariants:
    #   - _countries != {}
    #   - _indicators != Set()
    #   - regional_groups != {}
    _countries: Dict[str, Country]
    _indicators: Set[str]
    _regional_groups: Dict[str, Dict[str, Set[str]]]

    def __init__(self, air_filepath: str) -> None:
        """Initialize the simulator.

        The PM2.5 air pollution data file is required to initialize.
        Other data can be added later on.

        Preconditions:
            - The data file follows the format described in the report.
        """
        self._countries = {}
        self._indicators = set()
        self._regional_groups = data_extract.create_region_group_data()
        self.load_data(air_filepath, 'air pollution')

    def load_data(self, filepath: str, indicator_name: str) -> bool:
        """Load the data file into the simulator to populate the _countries
        dictionary.
        Add any new indicator into the set self._indicators.

        Returns whether if the data handling process is successful.

        Preconditions:
            - indicator_name is str
            - indicator_name != ''
            - indicator_name == indicator_name.lower()
        """

        with open(filepath) as file:
            reader = csv.reader(file)

            header = next(reader)
            world_map = data_extract.create_world_geo_from_json('Data/country_by_region.json')
            for row in reader:
                code = row[1]

                if code not in self._countries and code in world_map:
                    name = row[0]
                    region = world_map[code]['region']
                    sub_reg = world_map[code]['sub-region']
                    int_reg = world_map[code]['int-region']
                    self._countries[code] = Country(name, code, (region, sub_reg, int_reg))
                if code in world_map:
                    country_data = data_extract.read_formatted_row(row, header)
                    self._countries[code].add_data(indicator_name, country_data)

        self._indicators.add(indicator_name)
        return True

    def get_gapminder_data_from_regions(self, years: List[int], *indicators: str,
                                        region_type: Optional[str] = 'region',
                                        regions: Optional[Set[str]] = None) -> \
            Dict[int, Dict[str, List[Any]]]:
        """Returns a dictionary of data collected from the countries in the given regions.
            The keys of this dictionary are the years of the data, and the associated values
            are dictionaries with:
                - Keys are either 'name', 'region' or an indicator.
                - Values are lists of data values. All of these list have the same
                order, which is based on the order of the list correspond to 'name'.

        Preconditions:
            - region_type in {'region', 'sub-region'}
            - all(year in range(1990, 2021) for year in years)
            - all(indicator in self._indicators for indicator in indicators)
            - 'population' in indicators
            - all(region in self._regional_groups[region_type] for region in regions)
            - regions can be all sub-regions or all regions, but cannot be mixed.
        """
        indicators = list(indicators) + ['name', 'region']
        # Accumulator
        data = {year: {indicator: [] for indicator in indicators} for year in years}
        if regions is None:     # then get the data of the whole world.
            regions = set(reg for reg in self._regional_groups[region_type])

        for region in regions:
            for country_code in self._regional_groups[region_type][region]:
                if country_code in self._countries:
                    update_gapminder_data(data, years, self._countries[country_code],
                                          region_type, *indicators)

        if not data[years[0]]['population']:
            raise NoDataPointsException

        return data

    def get_data_points(self, years: List[int], indicator1: str, indicator2: str,
                        region: Optional[str] = None) -> List[Tuple[float, float]]:
        """Returns the list of data points of the given years with the given indicators.
        All data points available from every country will be returned.

        Returns an empty list if there's no data.

        Preconditions:
            - indicator1 != '' and indicator2 != ''
            - indicator1 != indicator2
            - region is None or region in self_regional_group['region'] or \
            region in self_regional_group['sub-region']
        """
        # Accumulator
        data_so_far = []
        if region is None:
            for country in self._countries.values():
                data_so_far += country.get_data_points(years, indicator1, indicator2)
        elif region in self._regional_groups['region']:
            for code in self._regional_groups['region'][region]:
                if code in self._countries:
                    data_so_far += self._countries[code].get_data_points(years, indicator1,
                                                                         indicator2)
        else:
            for code in self._regional_groups['sub-region'][region]:
                if code in self._countries:
                    data_so_far += self._countries[code].get_data_points(years, indicator1,
                                                                         indicator2)

        return data_so_far

    def get_country_name_list(self) -> List[Tuple[str, str]]:
        """Returns the list of country name and country code in alphabetical order"""
        return sorted([(self._countries[code].name, code)
                       for code in self._countries], key=lambda tup: tup[0])

    def indicators(self) -> Set[str]:
        """Returns a copy of the set of indicators."""
        return self._indicators.copy()

    def get_regions(self) -> List[str]:
        """Returns a sorted list of all regions."""
        return sorted([region for region in self._regional_groups['region']])

    def get_subregions(self) -> List[str]:
        """Returns a sorted list of all sub-regions."""
        return sorted([subregion for subregion in self._regional_groups['sub-region']])


class NoDataPointsException(Exception):
    """Exception raises when attempting to perform calculations on empty lists
    of data points."""
    def __str__(self) -> str:
        return "No data points."


# Helper function
def update_gapminder_data(data: dict, years: List[int], country: Country,
                          region_type: str, *indicators) -> None:
    """Mutate the data dictionary by adding data obtained from the country in the given
    years.

    Preconditions:
        - all(year in data for year in years)
        - all('population' in data[year] for year in years)
        - 'population' in indicators
        - region_type in {'region', 'sub-region'}
    """
    # Accumulator
    temp_data = {}
    for indicator in indicators:
        temp_data[indicator] = country.get_data_values(years, indicator)

    min_pop = 8913
    max_pop = 1397715000

    if any({temp_data[ind] == [] and ind not in {'region', 'name'}
            for ind in indicators}):
        return  # Immediately return, so the data will not be updated.
    country_name = country.name
    region = country.region[region_type]
    for i in range(len(years)):
        # Rescale population to the range 120-130 to later match with circle radius
        cur_pop = (((temp_data['population'][i] - min_pop) * 120) / (max_pop - min_pop)) + 10
        list.append(data[years[i]]['population'], cur_pop)
        list.append(data[years[i]]['region'], region)
        list.append(data[years[i]]['name'], country_name)
        for indicator in indicators:
            if indicator not in {'population', 'region', 'name'}:
                list.append(data[years[i]][indicator], temp_data[indicator][i])


if __name__ == '__main__':
    manager = DataManager('Data/air_quality_formatted.csv')
    from presentation import load_data

    load_data(manager)
    years = [1990, 1995, 2000, 2005] + list(range(2010, 2018))
    data = manager.get_gapminder_data_from_regions(years, 'population', 'gdp per capita', 'air pollution')