''' Prepare data, regardless of survey period, for analysis. '''
import sys
import os
import re
import pickle

import pandas as pd
import numpy as np

from datetime import datetime
from classes import Ego, Alter


def read_input_files(input_files, header=None):
    if header:
        return [pd.read_csv(file, sep=None, engine='python',
                header=0, names=header) for file in input_files]
    else:
        return [pd.read_csv(file, sep=None, engine='python') for file in
                input_files]


def rename_variables(data):
    data.columns = [re.sub('\s', '_', names) for
                    names in data.columns.tolist()]
    return data


def change_to_missing(data):
    return data.applymap(lambda x: np.nan if x<0 else x)


def convert_dates(data, variable):
    mth = [mth.group(0)[:3] if mth is not None else '' for mth in
           data[variable].apply(lambda x: re.search('[A-Za-z]{1,}',
           x)).tolist()]
    yr = [yr.group(0) if yr is not None else '' for yr in
          data[variable].apply(lambda x: re.search('\d{2,}',
          x)).tolist()]
    return [datetime.strptime('01{}{}'.format(m, y), '%d%b%Y') if m is not
            '' else np.nan for m, y in zip(mth, yr)]


def main(config):
    # read in data and rename columns
    ego = rename_variables(pd.concat(read_input_files(config.ego_input_files)))
    alt = rename_variables(pd.concat(read_input_files(config.alt_input_files)))


    # change uncollected data to missing (np.nan)
    ego = change_to_missing(ego)
    alt = change_to_missing(alt)

    # make survey-dependent changes
    if config.name=='baseline':
        # read in cd4 count updates
        cd4 = pd.concat(read_input_files(config.cd4_input_files,
                        header=['Egoid', 'cd4']))

        # clean variables
        ego.EgoGender = ego.EgoGender.apply(lambda x: 0 if x==2 else x)
        ego.rename(columns={'EgoGender': 'male'}, inplace=True)

        ego.EgoStartCare = convert_dates(ego, 'EgoStartCare')
        ego.EgoDateTestPoz = convert_dates(ego, 'EgoDateTestPoz')

        # fixup start care year for a couple of ego's (bad dates discovered by
        # hand)
        ego.EgoStartCare[(ego.EgoID==385) |
                         (ego.EgoID==392)] == datetime.strptime('01Dec2010',
                         '%d%b%Y')
        ego.EgoStartCare[(ego.EgoID==349) |
                         (ego.EgoID==392)] == datetime.strptime('01Jan2011',
                         '%d%b%Y')

        # variable creation
        ego['mths_treatment'] = (datetime.strptime('01Sep2011', '%d%b%Y') -
                                ego.EgoStartCare) / np.timedelta64(1, 'M')
        ego['yrs_positive'] = (datetime.strptime('01Sep2011', '%d%b%Y') -
                                ego.DateTestPoz) / np.timedelta64(1, 'Y')

    elif config.name=='midline':
        cd4 = pd.concat(read_input_files(config.cd4_input_files,
                        header=['Egoid', 'cd4']))
        cd4 = cd4[cd4.cd4>0]
    else:
        pass

    # create ego and alter classes
    ego = [Ego(group, id) for id, group in ego.groupby('EgoID') if
           (len(group)>1) & ((id>=300) & (id<=475)) |
           ((id>=500) & (id<=526))]
    alt = [Alter(group, id) for id, group in alt.groupby('EgoID') if
           (len(group)>1) & ((id>=300) & (id<=475)) |
           ((id>=500) & (id<=526))]

    # save data
    pickle.dump([ego, alt], open('{}/{}'.format(config._path_to_data,
                'baseline.pkl'), 'wb'))


class Config(object):
    _path_to_data = os.getcwd()


    @property
    def ego_input_files(self):
        return ['{}{}{}'.format(self._path_to_data, self._data_dir, fname) for
                fname in self._ego_inputs]

    @property
    def alt_input_files(self):
        return ['{}{}{}'.format(self._path_to_data, self._data_dir, fname) for
                fname in self._alt_inputs]

    @property
    def cd4_input_files(self):
        return ['{}{}{}'.format(self._path_to_data, self._data_dir, fname) for
                fname in self._cd4_inputs]

class BaselineConfig(Config):
    name = 'baseline'
    _data_dir = '/data/m0/'
    _ego_inputs = ['ego_pt1.csv', 'ego_pt2.csv']
    _alt_inputs = ['alter_pt1.csv', 'alter_pt2.csv']
    _cd4_inputs = ['missing_cd4.txt']


class MidlineConfig(Config):
    name = 'midline'
    _data_dir = '/data/m6/'
    _ego_inputs = ['ego_pt1.csv', 'ego_pt2.csv']
    _alt_inputs = ['alter_pt1.csv', 'alter_pt2.csv']
    _cd4_inputs = ['original_cd4.csv', 'missing_cd4.csv']


class EndlineConfig(Config):
    name = 'endline'
    _data_dir = '/data/m12/'
    _ego_inputs = ['ego_pt1.csv', 'ego_pt2.csv']
    _alt_inputs = ['alter_pt1.csv', 'alter_pt2.csv']


if __name__ == '__main__':
    data_config = {
        'm0': BaselineConfig(),
        'm6': MidlineConfig(),
        'm12': EndlineConfig(),
    }
    main(data_config[sys.argv[1]])
