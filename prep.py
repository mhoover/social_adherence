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
          data[variable].apply(lambda x: re.search('\d{3,}',
          x)).tolist()]
    return [datetime.strptime('01{}{}'.format(m, y), '%d%b%Y') if m is not
            '' else np.nan for m, y in zip(mth, yr)]


def make_dichotomous(variable, **kwargs):
    if pd.isnull(variable):
        return np.nan
    else:
        if 'dichot' in kwargs:
            return 1 if variable>kwargs['dichot'] else 0
        elif 'one' in kwargs:
            if variable in kwargs['one']:
                return 1
            else:
                return 0
        else:
            sys.exit('Invalid parameter; please try again.')


def disclosure_status(data):
    if (pd.isnull(data.KnowAlterStatus)) & (pd.isnull(data.AlterKnowStatus)):
        return np.nan
    elif (data.KnowAlterStatus==1) & (data.AlterKnowStatus==1):
        return 1
    else:
        return 0


def main(config):
    # read in data and rename columns
    ego = rename_variables(pd.concat(read_input_files(config.ego_input_files)))
    alt = rename_variables(pd.concat(read_input_files(config.alt_input_files)))

    # change uncollected data to missing (np.nan)
    ego = change_to_missing(ego)
    alt = change_to_missing(alt)

    ego['isolate'] = ego.Degree_centrality.apply(make_dichotomous,
                                                 dichot=0)
    ego['weekly_doses'] = ego.EgoDailyDoses * 7
    ego['weekly_adherence'] = 1.0 - ego.EgoWeeklyMissed/ego.weekly_doses
    ego.weekly_adherence = ego.weekly_adherence.apply(lambda x: np.nan if
                                                      x<0 else x)
    ego['support_receive'] = ego.EgoSupportReceiveNorm.apply(make_dichotomous,
                                                             one=[2, 3])
    ego['support_provide'] = ego.EgoSupportProvideNorm.apply(make_dichotomous,
                                                             one=[2, 3])
    ego['mutual_disclose'] = ego.apply(disclosure_status, axis=1)
    ego['active_disclose'] = ego.AlterKnowStatusHow.apply(make_dichotomous,
                                                          one=[1, 2, 3, 4, 5])
    # make survey-dependent changes
    if config.name!='endline':
        # change gender variable to unambiguous dichotomous variable
        ego.EgoGender = ego.EgoGender.apply(lambda x: 0 if x==2 else x)
        ego.rename(columns={'EgoGender': 'male'}, inplace=True)

        # reformat dates
        ego.EgoStartCare = convert_dates(ego, 'EgoStartCare')
        ego.EgoDateTestPoz = convert_dates(ego, 'EgoDateTestPoz')

        # variable creation
        ego['mths_treatment'] = (datetime.strptime('01Sep2011', '%d%b%Y') -
                                ego.EgoStartCare) / np.timedelta64(1, 'M')
        ego['yrs_positive'] = (datetime.strptime('01Sep2011', '%d%b%Y') -
                                ego.EgoDateTestPoz) / np.timedelta64(1, 'Y')

        # merge in cd4 counts
        cd4 = pd.concat(read_input_files(config.cd4_input_files,
                                         header=['EgoID', 'cd4']))
        cd4 = cd4[cd4.cd4>0]
        ego = ego.merge(cd4, on='EgoID', how='left')
        ego.EgoCD4 = ego.apply(lambda x: x.cd4 if pd.isnull(x.EgoCD4) else
                               x.EgoCD4, axis=1)
        ego.drop('cd4', axis=1, inplace=True)

    if config.name=='baseline':
        # fixup start care year for a couple of ego's
        ego.EgoStartCare[(ego.EgoID==385) |
                         (ego.EgoID==392)] == datetime.strptime('01Dec2010',
                         '%d%b%Y')
        ego.EgoStartCare[(ego.EgoID==349) |
                         (ego.EgoID==392)] == datetime.strptime('01Jan2011',
                         '%d%b%Y')
    elif config.name=='midline':
        # delete additional records
        ego.drop_duplicates(['EgoID', 'Alter_number', 'Alter_name'],
                            inplace=True)
        alt.drop_duplicates(['EgoID', 'Alter_1_number', 'Alter_2_number'],
                            inplace=True)
    elif config.name=='endline':
        # read in alter follow-up surveys
        alt_followup = rename_variables(pd.concat(read_input_files(
                                        config.alt_followup_input_files)))

        # variable clean up
        ego.EgoIncome = ego.EgoIncome.apply(lambda x: np.nan if x=='Business'
                                          else int(x))

    # create ego and alter classes
    ego = [Ego(group, id) for id, group in ego.groupby('EgoID') if
           (len(group)>1) & ((id>=300) & (id<=475)) |
           ((id>=500) & (id<=526))]
    alt = [Alter(group, id) for id, group in alt.groupby('EgoID') if
           (len(group)>1) & ((id>=300) & (id<=475)) |
           ((id>=500) & (id<=526))]

    # save data
    # pickle.dump([ego, alt], open('{}/{}.pkl'.format(config._path_to_data,
    #             config.name), 'wb'))


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

    @property
    def alt_followup_input_files(self):
        return ['{}{}{}'.format(self._path_to_data, self._data_dir, fname) for
                fname in self._alt_followup_inputs]


class BaselineConfig(Config):
    name = 'baseline'
    _data_dir = '/data/m0/'
    _ego_inputs = ['ego_pt1.csv', 'ego_pt2.csv']
    _alt_inputs = ['alter_pt1.csv', 'alter_pt2.csv']
    _cd4_inputs = ['missing_cd4.txt']


class MidlineConfig(Config):
    name = 'midline'
    _data_dir = '/data/m6/'
    _ego_inputs = ['ego_pt1.csv', 'ego_pt2.csv', 'ego_pt3.csv',
                   'ego_pt4.csv', 'ego_pt5.csv', 'ego_pt6.csv']
    _alt_inputs = ['alter_pt1.csv', 'alter_pt2.csv', 'alter_pt3.csv',
                   'alter_pt4.csv', 'alter_pt5.csv', 'alter_pt6.csv']
    _cd4_inputs = ['original_cd4.csv', 'missing_cd4.csv']


class EndlineConfig(Config):
    name = 'endline'
    _data_dir = '/data/m12/'
    _ego_inputs = ['ego_pt1.csv', 'ego_pt2.csv', 'ego_pt3.csv', 'ego_pt4.csv',
                   'ego_pt5.csv', 'ego_pt6.csv', 'ego_pt7.csv', 'ego_pt8.csv',
                   'ego_pt9.csv', 'ego_pt10.csv', 'ego_pt11.csv',
                   'ego_pt12.csv', 'ego_pt13.csv', 'ego_pt14.csv']
    _alt_inputs = ['alter_pt1.csv', 'alter_pt2.csv', 'alter_pt3.csv',
                   'alter_pt4.csv', 'alter_pt5.csv', 'alter_pt6.csv',
                   'alter_pt7.csv', 'alter_pt8.csv', 'alter_pt9.csv',
                   'alter_pt10.csv', 'alter_pt11.csv', 'alter_pt12.csv',
                   'alter_pt13.csv', 'alter_pt14.csv']
    _alt_followup_inputs = ['alter_followup_pt1.csv', 'alter_followup_pt2.csv',
                            'alter_followup_pt3.csv', 'alter_followup_pt4.csv',
                            'alter_followup_pt5.csv']


if __name__ == '__main__':
    data_config = {
        'm0': BaselineConfig(),
        'm6': MidlineConfig(),
        'm12': EndlineConfig(),
    }
    main(data_config[sys.argv[1]])
