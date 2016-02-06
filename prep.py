''' Prepare data, regardless of survey period, for analysis. '''
import sys
import os
import re
import pickle

import pandas as pd
import numpy as np

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


def main(config):
    # read in data and rename columns
    ego = rename_variables(pd.concat(read_input_files(config.ego_input_files)))
    alt = rename_variables(pd.concat(read_input_files(config.alt_input_files)))

    # read in cd4 data, which is survey-dependent
    if config.name=='baseline':
        cd4 = pd.concat(read_input_files(config.cd4_input_files,
                        header=['Egoid', 'cd4']))
    elif config.name=='midline':
        cd4 = pd.concat(read_input_files(config.cd4_input_files,
                        header=['Egoid', 'cd4']))
        cd4 = cd4[cd4.cd4>0]

    # change uncollected data to missing (np.nan)
    ego = change_to_missing(ego)
    alt = change_to_missing(alt)

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
