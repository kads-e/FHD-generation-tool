from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np
from scipy.optimize import linear_sum_assignment

def match_stars(in_blau, in_gruen, max_sep_arcsec=3):
    blau = SkyCoord(
        ra=[row[3] for row in in_blau] * u.deg,
        dec=[row[4] for row in in_blau] * u.deg,
        frame="icrs",
    )
    gruen = SkyCoord(
        ra=[row[3] for row in in_gruen] * u.deg,
        dec=[row[4] for row in in_gruen] * u.deg,
        frame="icrs",
    )

    cost = blau[:, None].separation(gruen[None, :]).arcsec
    cost[cost > max_sep_arcsec] = 1e9

    rows, cols = linear_sum_assignment(cost)

    return [
        (int(row), int(col))
        for row, col in zip(rows, cols)
        if cost[row, col] <= max_sep_arcsec
    ]


def remove_common_first_digit(array, tuple_index):
    """Remove a shared first digit from one entry in every tuple.

    The input array is changed in place.  ``False`` is returned when the
    selected entry is invalid, empty, or does not start with the same digit
    in every row.
    """
    if len(array) == 0:
        return False

    try:
        values = [row[tuple_index] for row in array]
    except (IndexError, TypeError):
        return False

    if not all(isinstance(value, str) and value for value in values):
        return False

    first_digit = values[0][0]
    if not first_digit.isdigit():
        return False
    if not all(value[0] == first_digit for value in values):
        return False

    for row_index, row in enumerate(array):
        new_value = row[tuple_index][1:]
        if isinstance(row, tuple):
            array[row_index] = row[:tuple_index] + (new_value,) + row[tuple_index + 1:]
        else:
            row[tuple_index] = new_value

    return True