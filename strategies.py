''' Define classes and methods for use with processing of the Uganda
social adherence data for the baseline (m0), midline (six months - m6),
and endline (twelve months - m12) surveys '''

class Ego(object):
    ''' The focal person of a survey. This is the person answering
    questions in the survey, nominating connections (alters)
    around them, and indicating how alters are connected together.

    An ego has the following attributes:

    '''

    def __init__(self, data, id):
        self.data = data
        self.id = id

    def len(self):
        return len(self.data)


class Alter(Ego):
    ''' The network members of an ego. Each set of alters matches
    back to a particular ego in the survey.

    An alter has the following attributes:

    '''

    def __init__(self, data, ego_id, alt_id):
        self.data = data
        self.ego_id = ego_id
        self.alt_id = alt_id
