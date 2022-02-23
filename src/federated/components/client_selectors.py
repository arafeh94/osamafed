import random
from typing import List

from src.federated.federated import FederatedLearning
from src.federated.protocols import ClientSelector


class All(ClientSelector):
    def select(self, trainer_ids: List[int], context: FederatedLearning.Context) -> List[int]:
        return trainer_ids


class Random(ClientSelector):
    def __init__(self, num):
        self.num = num

    def select(self, trainer_ids: List[int], context: FederatedLearning.Context) -> List[int]:
        select_size = self.num
        if self.num <= 1:
            select_size = int(self.num * len(trainer_ids))
        select_size = 1 if select_size < 1 else select_size
        selected_trainers = random.sample(trainer_ids, select_size)
        return selected_trainers


class Specific(ClientSelector):
    def __init__(self, mapping: [[]]):
        """

        Args:
            mapping: a 2D array, for each round, which clients are selected. Ex: [[1,2],[4,5]]
        """
        self.mapping = mapping

    def select(self, trainer_ids: List[int], context: FederatedLearning.Context) -> List[int]:
        return self.mapping[context.round_id % len(self.mapping)]
