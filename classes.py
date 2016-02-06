''' Define classes and methods for use with processing of the Uganda
social adherence data for the baseline (m0), midline (six months - m6),
and endline (twelve months - m12) surveys '''

class Ego(object):
    ''' The focal person of a survey. This is the person answering
    questions in the survey, nominating connections (alters)
    around them, and indicating how alters are connected together.

    An ego has the following attributes:
        data: the data collected from a particular ego
        ego_id: the ego's unique identifying number (integer)
    '''

    def __init__(self, data, ego_id):
        self.data = data
        self.ego_id = ego_id


    def num_alters(self):
        return len(self.data)


class Alter(Ego):
    ''' The network members of an ego. Each set of alters matches
    back to a particular ego in the survey.

    An alter has the following attributes:
        data: the data collected on the alter from the ego
        ego_id: the identifier for which ego the alters belong to
    '''

    def __init__(self, data, ego_id):
        self.data = data
        self.ego_id = ego_id


    def connected_pairs(self):
        try:
            return {self.data['EgoID'].min():
                    self.data[self.data['Structure']==2].apply(lambda x:
                    (x['Alter 1 name'], x['Alter 2 name']),
                    axis=1).tolist()}
        except:
            return {self.data['EgoID'].min(): None}
