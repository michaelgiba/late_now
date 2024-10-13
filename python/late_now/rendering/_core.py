from abc import ABC, abstractmethod


class Updater(ABC):
    @abstractmethod
    def update(self, frame_index: int):
        raise NotImplementedError()


class CompositeUpdater(Updater):
    def __init__(self, *updaters):
        self.updaters = list(updaters)

    def update(self, frame_index: int):
        for updater in self.updaters:
            updater.update(frame_index)
