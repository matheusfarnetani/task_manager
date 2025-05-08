# task_manager/service/generic_service.py

from typing import TypeVar, Generic, Optional, List
from task_manager.repository.interface import ITaskRepository

T = TypeVar("T")

class GenericService(Generic[T]):
    def __init__(self, repository: ITaskRepository):
        self.repo = repository

    def get_all(self) -> List[T]:
        return self.repo.list_all()

    def get_by_guid(self, guid: str) -> Optional[T]:
        return self.repo.get_by_guid(guid)

    def create(self, entity: T) -> None:
        self.repo.add(entity)

    def update(self, entity: T) -> None:
        self.repo.update(entity)

    def delete(self, guid: str) -> None:
        self.repo.delete(guid)
