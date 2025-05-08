# task_manager/repository/interface.py

from abc import ABC, abstractmethod
from typing import List, Optional

from task_manager.domain.task import Task


class ITaskRepository(ABC):

    @abstractmethod
    def list_all(self) -> List[Task]:
        pass

    @abstractmethod
    def get_by_guid(self, guid: str) -> Optional[Task]:
        pass

    @abstractmethod
    def add(self, task: Task) -> None:
        pass

    @abstractmethod
    def update(self, task: Task) -> None:
        pass

    @abstractmethod
    def delete(self, guid: str) -> None:
        pass
