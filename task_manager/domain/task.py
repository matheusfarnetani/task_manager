# task_manager/domain/task.py

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import uuid

from .todo_item import ToDoItem
from .state import State


@dataclass
class Task:
    guid: str
    title: str
    position: int
    state: State
    deadline: datetime
    created_at: datetime
    description: Optional[str] = None
    responsible: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_by: Optional[str] = None
    todo: List[ToDoItem] = field(default_factory=list)

    def is_complete(self) -> bool:
        if self.state == State.COMPLETED:
            return True
        return all(item.completed for item in self.todo)

    def mark_complete(self):
        self.state = State.COMPLETED
        self.completed_at = datetime.now()
        for item in self.todo:
            item.mark_complete()

    def add_todo_item(self, item: ToDoItem):
        item.position = len(self.todo) + 1
        self.todo.append(item)

    def remove_todo_item(self, item_guid: str):
        self.todo = [item for item in self.todo if item.guid != item_guid]
        self._normalize_positions()

    def reorder_item(self, item_guid: str, new_position: int):
        item = next((i for i in self.todo if i.guid == item_guid), None)
        if item is None:
            raise ValueError("Item not found")
        self.todo.remove(item)
        self.todo.insert(new_position - 1, item)
        self._normalize_positions()

    def _normalize_positions(self):
        for i, item in enumerate(self.todo, start=1):
            item.position = i

    def todo_count(self) -> int:
        return len(self.todo)

    def get_todo_by_position(self, position: int) -> ToDoItem:
        for item in self.todo:
            if item.position == position:
                return item
        raise ValueError(f"ToDoItem at position {position} not found.")

    def __str__(self):
        todo_lines = "\n  ".join(
            [f"[{'x' if item.completed else ' '}] {item.position}. {item.text}" for item in sorted(
                self.todo, key=lambda t: t.position)]
        )
        return (
            f"Task: {self.title} (GUID: {self.guid})\n"
            f"  Description: {self.description}\n"
            f"  State: {self.state.name}\n"
            f"  Position: {self.position}\n"
            f"  Responsible: {self.responsible}\n"
            f"  Todo items:\n  {todo_lines if self.todo else 'No items'}\n"
            f"  Deadline: {self.deadline.isoformat()}\n"
            f"  Created by: {self.created_by}\n"
            f"  Created at: {self.created_at.isoformat()}\n"
            f"  Completed at: {self.completed_at.isoformat() if self.completed_at else 'Not completed'}"
        )

    @staticmethod
    def create(
        title: str,
        position: int,
        state: State,
        deadline: datetime,
        created_by: Optional[str],
        responsible: Optional[str] = None,
        description: Optional[str] = None,
        todo: Optional[List[ToDoItem]] = None
    ) -> "Task":
        if not title or not isinstance(title, str):
            raise ValueError("Title must be a non-empty string")
        if position < 1:
            raise ValueError("Position must be >= 1")
        if not isinstance(state, State):
            raise ValueError("Invalid task state")
        if not isinstance(deadline, datetime):
            raise ValueError("Deadline must be a datetime object")

        return Task(
            guid=str(uuid.uuid4()),
            title=title,
            position=position,
            state=state,
            deadline=deadline,
            created_at=datetime.now(),
            created_by=created_by,
            responsible=responsible,
            description=description,
            completed_at=None,
            todo=todo or [],
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            guid=data["guid"],
            title=data["title"],
            position=data["position"],
            state=State(data["state"]),
            deadline=datetime.fromisoformat(data["deadline"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            completed_at=datetime.fromisoformat(
                data["completed_at"]) if data.get("completed_at") else None,
            created_by=data.get("created_by"),
            responsible=data.get("responsible"),
            description=data.get("description"),
            todo=[ToDoItem.from_dict(item) for item in data.get("todo", [])],
        )

    def to_dict(self) -> dict:
        return {
            "guid": self.guid,
            "title": self.title,
            "position": self.position,
            "state": self.state.value,
            "deadline": self.deadline.isoformat(),
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_by": self.created_by,
            "responsible": self.responsible,
            "description": self.description,
            "todo": [item.to_dict() for item in self.todo],
        }
