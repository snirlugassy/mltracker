from dataclasses import dataclass

from mltracker.core.tracked_object import TrackedObject
from mltracker.core.experiment import Experiment


@dataclass
class Run(TrackedObject):
    __table__ = "run"

    id: int
    experiment: int
    name: str
    params: dict
    created_at: float
    updated_at: float
