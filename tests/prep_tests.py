''' Tests for prep functions '''
import pytest

import pandas as pd

from prep import *


df = pd.DataFrame({'Col 1': [1] * 3,
                   'Col2': [2] * 3,
                  })

# def test_read_input_files(input_files, header=None):
#     pass

@pytest.mark.parametrize('test, expected',[
    (df, ['Col_1', 'Col2'])
])
def test_rename_variables(test, expected):
    result = rename_variables(test)

    assert result.columns.tolist() == expected


# def test_change_to_missing(data):
#     pass


# def test_convert_dates(data, variable):
#     pass


# def test_make_dichotomous(variable, **kwargs):
#     pass


# def test_disclosure_status(data):
#     pass
