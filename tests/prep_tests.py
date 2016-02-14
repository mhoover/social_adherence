''' Tests for prep functions '''
import pytest

import pandas as pd
import numpy as np

from datetime import datetime
from prep import *


df1 = pd.DataFrame({'Col 1': [1, -1] * 2})
df2 = pd.DataFrame({'Col2': [2, np.nan] * 2})
df3 = pd.DataFrame({'var1': ['Sep 12 2015', 'September  2015', 'sep 1 2015'],
                    'var2': ['1 Dec 2014', '1 December 2014', 'Dec. 12 2014'],
                    'var3': ['August 2012 2011', 'aug 2012', '2012 2011'],
                   })
df4 = pd.DataFrame({'v1': [0, .01, .04, .09, .99, 1],
                    'v2': [1, 2, 3, 4, 5, 6],
                   })
df5 = pd.DataFrame({'KnowAlterStatus': [1, 1, 0, 0, np.nan],
                    'AlterKnowStatus': [1, 0, 1, 0, np.nan],
                   })

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


@pytest.mark.parametrize('test_data, var, expected', [
    (df3, 'var1', [datetime.strptime('01Sep2015', '%d%b%Y'),
                   datetime.strptime('01Sep2015', '%d%b%Y'),
                   datetime.strptime('01Sep2015', '%d%b%Y'),
                  ]),
    (df3, 'var2', [datetime.strptime('01Dec2014', '%d%b%Y'),
                   datetime.strptime('01Dec2014', '%d%b%Y'),
                   datetime.strptime('01Dec2014', '%d%b%Y'),
                  ]),
    (df3, 'var3', [datetime.strptime('01Aug2012', '%d%b%Y'),
                   datetime.strptime('01Aug2012', '%d%b%Y'),
                   np.nan,
                  ]),
])
def test_convert_dates(test_data, var, expected):
    result = convert_dates(test_data, var)

    assert result == expected


@pytest.mark.parametrize('test_data, var, val, expected', [
    (df4, 'v1', .04, [0, 0, 0, 1, 1, 1]),
])
def test_make_dichotomous(test_data, var, val, expected):
    result = test_data[var].apply(make_dichotomous, dichot=val)

    assert all(result == expected)


@pytest.mark.parametrize('test_data, var, val, expected', [
    (df4, 'v2', [4, 5, 6], [0, 0, 0, 1, 1, 1]),
])
def test_make_dichotomous(test_data, var, val, expected):
    result = test_data[var].apply(make_dichotomous, one=val)

    assert all(result == expected)


@pytest.mark.parametrize('test, expected', [
    (df5, [1, 0, 0, 0, np.nan]),
 ])
def test_disclosure_status(test, expected):
    result = test.apply(disclosure_status, axis=1)

    np.testing.assert_equal(result.tolist(), expected)
