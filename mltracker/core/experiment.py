from dataclasses import dataclass

from mltracker.core.tracked_object import TrackedObject


@dataclass
class Experiment(TrackedObject):
    __table__ = "experiment"

    id: int
    name: str
    created_at: float
    updated_at: float
