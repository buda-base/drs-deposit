class SprocColumnError(ValueError):

    def __init__(self, *args):
        super(SprocColumnError, self).__init__(*args)
