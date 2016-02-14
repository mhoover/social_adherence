''' Tests for prep functions '''
import pytest

import pandas as pd
import numpy as np

from prep import *


df1 = pd.DataFrame({'Col 1': [1, -1] * 2})
df2 = pd.DataFrame({'Col2': [2, np.nan] * 2})

# def test_read_input_files(input_files, header=None):
#     pass

@pytest.mark.parametrize('test, expected', [
    (df1, ['Col_1']),
    (df2, ['Col2']),
])
def test_rename_variables(test, expected):
    result = rename_variables(test)

    assert result.columns.tolist() == expected


@pytest.mark.parametrize('test, expected', [
    (df1, [1, np.nan, 1, np.nan]),
    (df2, [2, np.nan, 2, np.nan]),
])
def test_change_to_missing(test, expected):
    result = change_to_missing(test)

    assert all(result == expected)


# def test_convert_dates(data, variable):
#     pass


# def test_make_dichotomous(variable, **kwargs):
#     pass


# def test_disclosure_status(data):
#     pass
