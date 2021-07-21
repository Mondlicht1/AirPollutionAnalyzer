"""
CSC110 Course Project: Air Pollution and Forestry
=========================================================================================
regression.py
This module provide functions for regressions and other calculations on data points.
=========================================================================================
@author: Tu Anh Pham
"""

import math
import random

from typing import List, Tuple


def convert_points(points: list) -> tuple:
    """Return a tuple of two lists, containing the x- and y-coordinates of the given points.

    Preconditions:
        - len(points) > 0
        - all(type(points[i][0]) is float and type(poins[i][1]) is float for i in points)

    """
    return ([p[0] for p in points], [p[1] for p in points])


def average(nums: list) -> float:
    """Return the average of the numbers in nums

    Preconditions:
        - len(nums) > 0
        - elements in nums are numeric.

    """

    return sum(nums) / len(nums)


def linear_regression(points: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Perform a linear regression on the given points.

    This function returns a pair of floats (a, b) such that the line
    y = a + bx is the approximation of this data.

    Preconditions:
        - points is a list of pairs of floats: [(x_1, y_1), (x_2, y_2), ...]
        - len(points) > 0
    """
    x = average([p[0] for p in points])
    y = average([p[1] for p in points])
    b = sum([(p[0] - x) * (p[1] - y) for p in points]) / sum([(p[0] - x) ** 2 for p in points])
    a = y - b * x

    return (a, b)


def exponential_regression(points: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Perform an exponential regression on the given points.

    Returns a tuple (a, b) where a, b are the coefficients in the curve of best fit
    equation y = ab^x.

    Preconditions:
        - points is a list of pairs of floats: [(x_1, y_1), (x_2, y_2), ...]
        - len(points) > 0
    """
    # The points in the form (x, log(y)):
    new_points = [(p[0], math.log10(p[1])) for p in points]

    slope, intercept = linear_regression(new_points)
    a = 10**intercept
    b = 10**slope

    return (a, b)


def least_square_exponential_regression(points: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Perform an exponential regression on the given points.

    Returns a tuple (a, b) where a, b are the coefficients in the curve of best fit
    equation y = ab^x.

    Preconditions:
        - points is a list of pairs of floats: [(x_1, y_1), (x_2, y_2), ...]
        - len(points) > 0
    """
    s_x2y = sum([(p[0] ** 2) * p[1] for p in points])
    s_ylny = sum([p[1] * math.log(p[1]) for p in points])
    s_xy = sum([p[0] * p[1] for p in points])
    s_xylny = sum([p[0] * p[1] * math.log(p[1]) for p in points])
    s_y = sum([p[1] for p in points])

    a = (s_x2y * s_ylny - s_xy * s_xylny) / (s_y * s_x2y - s_xy ** 2)
    b = (s_y * s_xylny - s_xy * s_ylny) / (s_y * s_x2y - s_xy ** 2)

    return (a, b)


def calculate_r_squared(points: list, a: float, b: float) -> float:
    """Return the R squared value when the given points are modelled as the line y = a + bx.

    points is a list of pairs of numbers: [(x_1, y_1), (x_2, y_2), ...]

    Preconditions:
        - points is not empty and contains tuples
        - each element of points is a tuple containing two floats

    """

    y = average([p[1] for p in points])

    tot = sum([(p[1] - y)**2 for p in points])
    res = sum([(p[1] - (a + b * p[0]))**2 for p in points])

    return 1 - (res / tot)


def evaluate_line(a: float, b: float, error: float, x: float) -> float:
    """Evaluate the linear function y = a + bx for the given a, b, and x values
    with the given error term.
    """
    return a + b * x + random.uniform(-error, error)


def evaluate_exponential_curve(a: float, b: float, error: float, x: float) -> float:
    """Evaluate the exponential curve exp(a)(e^(bx)) for the given a, b, and x values
    with the given error term.
    """
    return math.exp(a) * (math.e ** (b * x)) + random.uniform(-error, error)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['random', 'plotly.graph_objects'],
        'max-line-length': 100
    })
