# task_manager/service/task_service.py

from datetime import datetime, timedelta, timezone
import json
from typing import List, Literal, Optional

from task_manager.domain.state import State
from task_manager.domain.task import Task
from task_manager.domain.todo_item import ToDoItem
from task_manager.services.generic_service import GenericService
from task_manager.repository.interface import ITaskRepository


class TaskService(GenericService[Task]):
    def __init__(self, repository: ITaskRepository):
        super().__init__(repository)

    def create(self, entity: Task) -> None:
        super().create(entity)
        self._normalize_all_positions()

    def delete(self, guid: str) -> None:
        super().delete(guid)
        self._normalize_all_positions()

    def _normalize_all_positions(self) -> None:
        tasks = sorted(self.repo.list_all(), key=lambda t: t.position)
        for index, task in enumerate(tasks, start=1):
            task.position = index
        self.repo.update_all(tasks)

    def _get_task_or_error(self, guid: str) -> Task:
        task = self.repo.get_by_guid(guid)
        if not task:
            raise ValueError("Task not found")
        return task

    def _get_todo_or_error(self, task: Task, item_guid: str) -> ToDoItem:
        item = next((t for t in task.todo if t.guid == item_guid), None)
        if not item:
            raise ValueError("ToDoItem not found")
        return item

    def add_todo(self, task_guid: str, item: ToDoItem) -> None:
        task = self._get_task_or_error(task_guid)
        task.add_todo_item(item)
        self.repo.update(task)

    def remove_todo(self, task_guid: str, item_position: int) -> None:
        task = self._get_task_or_error(task_guid)
        item = task.get_todo_by_position(item_position)
        task.remove_todo_item(item.guid)
        self.repo.update(task)

    def reorder_todo(self, task_guid: str, item_position: int, new_position: int) -> None:
        task = self._get_task_or_error(task_guid)
        item = task.get_todo_by_position(item_position)
        task.reorder_item(item.guid, new_position)
        self.repo.update(task)

    def mark_task_complete(self, task_guid: str) -> None:
        task = self._get_task_or_error(task_guid)
        task.mark_complete()
        self.repo.update(task)

    def mark_todo_complete(self, task_guid: str, item_position: int) -> None:
        task = self._get_task_or_error(task_guid)
        item = task.get_todo_by_position(item_position)
        item.mark_complete()
        self.repo.update(task)

    def count(self) -> int:
        return self.repo.count()

    def update_task(self, task_guid: str, **kwargs) -> None:
        task = self._get_task_or_error(task_guid)

        for field, value in kwargs.items():
            if hasattr(task, field):
                setattr(task, field, value)
            else:
                raise AttributeError(f"Invalid field '{field}' for Task")

        # Ensure consistency if completed_at is set without COMPLETED state
        if task.completed_at and task.state != State.COMPLETED:
            raise ValueError(
                "Cannot set 'completed_at' if task is not marked as COMPLETED.")

        # Normalize task positions if 'position' was updated
        if "position" in kwargs:
            self._normalize_all_positions()

        self.repo.update(task)

    def set_state(self, task_guid: str, state: State) -> None:
        task = self._get_task_or_error(task_guid)
        task.state = state
        self.repo.update(task)

    def move_task(self, task_guid: str, new_position: int) -> None:
        tasks = self.repo.list_all()
        task = self._get_task_or_error(task_guid)
        tasks = [t for t in tasks if t.guid != task_guid]
        tasks.insert(new_position - 1, task)

        for idx, t in enumerate(tasks, start=1):
            t.position = idx

        self.repo.replace_all(tasks)

    def get_todo_count(self, task_guid: str) -> int:
        task = self._get_task_or_error(task_guid)
        return task.todo_count()

    def filter_by_state(self, state: State, tasks: Optional[List[Task]] = None) -> List[Task]:
        tasks = tasks or self.repo.list_all()
        return [t for t in tasks if t.state == state]

    def filter_by_title(self, keyword: str, tasks: Optional[List[Task]] = None) -> List[Task]:
        tasks = tasks or self.repo.list_all()
        return [t for t in tasks if keyword.lower() in t.title.lower()]

    def filter_due_soon(self, days: int, tasks: Optional[List[Task]] = None) -> List[Task]:
        now = datetime.now(timezone.utc)
        tasks = tasks or self.repo.list_all()
        return [t for t in tasks if now <= t.deadline <= now + timedelta(days=days)]

    def sort_tasks(self, tasks: List[Task], by: Literal["position", "deadline"]) -> List[Task]:
        if by == "deadline":
            return sorted(tasks, key=lambda t: t.deadline)
        return sorted(tasks, key=lambda t: t.position)

    def to_json(self, tasks: List[Task]) -> str:
        return json.dumps([t.to_dict() for t in tasks], indent=2, default=str)
