from dataclasses import dataclass

from mltracker.core.tracked_object import TrackedObject
from mltracker.core.run import Run


@dataclass
class Metric(TrackedObject):
    __table__ = "metric"

    id: int
    run: int
    key: str
    value: float
    timestamp: float
