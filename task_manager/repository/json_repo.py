# task_manager/repository/json_repo.py

import json
import os
from typing import List, Optional

from task_manager.domain.task import Task
from task_manager.repository.interface import ITaskRepository


class JsonTaskRepository(ITaskRepository):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump([], f)

    def _read_all(self) -> List[Task]:
        with open(self.file_path, "r") as f:
            data = json.load(f)
            return [Task.from_dict(d) for d in data]

    def _write_all(self, tasks: List[Task]):
        with open(self.file_path, "w") as f:
            json.dump([t.to_dict() for t in tasks], f, indent=2)

    def list_all(self) -> List[Task]:
        return self._read_all()
    
    def update_all(self, tasks: List[Task]) -> None:
        self._write_all(tasks)

    def get_by_guid(self, guid: str) -> Optional[Task]:
        return next((t for t in self._read_all() if t.guid == guid), None)

    def add(self, task: Task) -> None:
        tasks = self._read_all()
        tasks.append(task)
        self._write_all(tasks)

    def update(self, task: Task) -> None:
        tasks = self._read_all()
        for i, t in enumerate(tasks):
            if t.guid == task.guid:
                tasks[i] = task
                break
        else:
            raise ValueError("Task not found for update")
        self._write_all(tasks)

    def delete(self, guid: str) -> None:
        tasks = [t for t in self._read_all() if t.guid != guid]
        self._write_all(tasks)

    def count(self) -> int:
        return len(self._read_all())
    
    def replace_all(self, tasks: List[Task]) -> None:
        self._write_all(tasks)

