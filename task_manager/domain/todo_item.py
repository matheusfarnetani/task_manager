# task_manager/domain/todo_item.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import uuid


@dataclass
class ToDoItem:
    guid: str
    text: str
    position: int
    completed: bool
    created_at: datetime
    completed_at: Optional[datetime]

    def mark_complete(self):
        if not self.completed:
            self.completed = True
            self.completed_at = datetime.now()

    @staticmethod
    def create(text: str) -> "ToDoItem":
        return ToDoItem(
            guid=str(uuid.uuid4()),
            text=text,
            position=0,  # Will be reassigned by `add_todo_item`
            completed=False,
            created_at=datetime.now(),
            completed_at=None,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "ToDoItem":
        return cls(
            guid=data["guid"],
            text=data["text"],
            position=data["position"],
            completed=data["completed"],
            created_at=datetime.fromisoformat(data["created_at"]),
            completed_at=datetime.fromisoformat(
                data["completed_at"]) if data.get("completed_at") else None,
        )

    def to_dict(self) -> dict:
        return {
            "guid": self.guid,
            "text": self.text,
            "position": self.position,
            "completed": self.completed,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
