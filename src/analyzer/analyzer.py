from abc import ABC


class Analyzer(ABC):
    def __init__(self, data):
        self.data = data

    def analyze(self):
        pass
