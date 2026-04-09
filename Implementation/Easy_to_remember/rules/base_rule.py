# This is an abstract class for rules
from abc import ABC, abstractmethod

class Rule(ABC):
    name: object

    # Returns score for the object
    @abstractmethod
    def score(self, object):
        pass