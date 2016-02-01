''' Prepare data, regardless of survey period, for analysis. '''
import sys
import os
import pandas as pd
import numpy as np

def read_input_files(input_files):
    return [pd.read_csv(file, sep=None, engine='python') for file in
            input_files]


def main(config):
    ego = pd.concat(read_input_files(config.ego_input_files))
    import pdb; pdb.set_trace()
    # stuff to go in here

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
    # basics go in here


class BaselineConfig(Config):
    _data_dir = '/data/m0/'
    _ego_inputs = ['ego_pt1.csv', 'ego_pt2.csv']
    _alt_inputs = ['alter_pt1.csv', 'alter_pt2.csv']
    # this is stuff for the baseline survey


class MidlineConfig(Config):
    _data_dir = '/data/m6/'
    # this is stuff for the midline survey


class EndlineConfig(Config):
    _data_dir = '/data/m12/'
    # this is stuff for the endline survey


if __name__ == '__main__':
    data_config = {
        'm0': BaselineConfig(),
        'm6': MidlineConfig(),
        'm12': EndlineConfig(),
    }
    if len(sys.argv) > 1 and sys.argv[1] in data_config:
        main(data_config[sys.argv[1]])
