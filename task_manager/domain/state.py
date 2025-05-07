# task_manager/domain/state.py
from enum import Enum

class State(Enum):
    PENDING = 1
    IN_PROGRESS = 2
    COMPLETED = 3
    FAILED = 4
    CANCELLED = 5
    PAUSED = 6