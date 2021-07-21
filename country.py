"""
CSC110 Course Project: Air Pollution and Forestry
=================================================
Country Class
A Country instance represent a single country.
=================================================
@author: Tu Anh Pham
"""
from __future__ import annotations
from typing import Dict, List, Tuple, Set


class Country:
    """A country in the simulator.

    Instance Attributes:
        - name: The name of the country.
        - code: The country code (ISO 3166-1 alpha-3 standard).
        - region: The mapping of region types to the region the country belongs to.

    Representation Invariants:
        - name != ''
        - code != ''
        - all(k in {'region', 'sub-region', 'int-region'} for k in region)
    """
    # Private Instance Attributes:
    #   - _data: A dictionary with keys are indicator names and values
    #   are dictionaries that map the recorded years with the indicated values.
    #
    # Private Representation Invariants:
    #   - _data != {}
    _data: Dict[str, Dict[int, float]]

    # Public Instance Attributes
    name: str
    code: str
    region: Dict[str, str]

    def __init__(self, name: str, code: str, regions: Tuple[str, str, str]) -> None:
        """Initialize the country object.
            - regions is a tuple of the region, the sub-region, and the intermediate
            region the country belongs to, respectively.

        Preconditions:
            - reg[0] != "" and reg[1] != ""
            - name != ""
            - code != ""
        """
        self._data = {}
        self.region = {}
        self.name = name
        self.code = code
        self.region['region'] = regions[0]
        self.region['sub-region'] = regions[1]
        self.region['int-region'] = regions[2]

    def add_data(self, indicator_name: str, data: Dict[int, float]) -> None:
        """Add data to the country object.
           Add new data if not present. Replace data when applicable.

        Preconditions:
            - indicator_name != ''
            - len(data) > 0
            - data follows the format {year: value}.
        """
        if indicator_name not in self._data:
            self._data[indicator_name] = {}

        for year in data:
            self._data[indicator_name][year] = data[year]

    def get_data_values(self, years: List[int], indicator: str) \
            -> List[float]:
        """Return a list of data values with the given indicator, in the order as the
        given years.

        Returns an empty list if there is no data in at least one year.
        """
        if indicator not in self._data:
            return []
        # Accumulator: The list of data points.
        data_values = []

        for year in years:
            if year in self._data[indicator]:
                data_values.append(self._data[indicator][year])
            else:
                return []

        return data_values

    def get_data_points(self, years: List[int],
                        indicator1: str, indicator2: str) -> List[Tuple[float, float]]:
        """Returns a list of data points. Each point is a tuple of float values in the same order
        as the input indicators.

        Preconditions:
            - years != []
            - indicator1 != '' and indicator2 != ''
            - indicator1 != indicator2
        """
        if indicator1 not in self._data or indicator2 not in self._data:
            return []

        # Accumulator
        points_so_far = []
        for year in years:
            if year in self._data[indicator1] and year in self._data[indicator2]:
                points_so_far.append((self._data[indicator1][year], self._data[indicator2][year]))

        return points_so_far

    def indicators(self) -> Set[str]:
        """Returns a set of all indicators of the data this country object currently has.
        """
        return set(self._data.keys())


class NoDataException(Exception):
    """Exception raises when requesting a non-existent datum of a country in a given year."""
    def __str__(self) -> str:
        return "No data value found."


if __name__ == '__main__':
    import doctest

    doctest.testmod(verbose=True)

    import python_ta

    python_ta.check_all(config={
        'max-line-length': 100
    })
