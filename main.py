# main.py

# from task_manager.cli.cli import run_cli

# if __name__ == "__main__":
#     run_cli()

from datetime import datetime, timedelta
from task_manager.domain.state import State
from task_manager.domain.task import Task
from task_manager.domain.todo_item import ToDoItem
from task_manager.repository.json_repo import JsonTaskRepository

# Initialize repo
repo = JsonTaskRepository("tasks.json")

# List existing tasks
tasks = repo.list_all()
print("Initial total tasks:", repo.count())
for task in tasks:
    print(f"- {task.title} ({task.state.name}) has {task.todo_count()} todos")

# Create a new task
print("\nCreating new task...")
new_task = Task.create(
    title="Demo Task",
    description="Just a test",
    position=repo.count() + 1,
    state=State.PENDING,
    deadline=datetime.now() + timedelta(days=7),
    created_by="Tester"
)

# Add some ToDoItems
new_task.add_todo_item(ToDoItem.create("Step one"))
new_task.add_todo_item(ToDoItem.create("Step two"))
new_task.add_todo_item(ToDoItem.create("Final step"))

print(f"\nNew task created:\n{new_task}")

# Reorder BEFORE marking complete
if new_task.todo_count() >= 2:
    second_id = new_task.todo[1].guid
    new_task.reorder_item(second_id, 1)

# Save to repo
repo.add(new_task)

# Reload task to confirm order was saved
retrieved = repo.get_by_guid(new_task.guid)
print("\nTask after reorder (before completion):")
print(retrieved)

# Manually change state to IN_PROGRESS
retrieved.state = State.IN_PROGRESS

# Mark a single ToDoItem as complete
if retrieved.todo_count() >= 3:
    last_item = retrieved.todo[2]
    print(f"\nMarking single item '{last_item.text}' as complete...")
    last_item.mark_complete()
    repo.update(retrieved)

    # Reload to confirm
    partial = repo.get_by_guid(retrieved.guid)
    print("\nTask after marking one todo item complete:")
    print(partial)

# Mark the task as complete
retrieved.mark_complete()
repo.update(retrieved)

# Reload again to show completed state
completed = repo.get_by_guid(retrieved.guid)
print("\nTask after marking complete:")
print(completed)

# Reorder AGAIN after completion
if completed.todo_count() >= 3:
    final_step_id = completed.todo[2].guid
    completed.reorder_item(final_step_id, 1)
    repo.update(completed)

# Final reload and print
final = repo.get_by_guid(completed.guid)
print("\nFinal task after second reorder (post-completion):")
print(final)

# Delete the task
repo.delete(final.guid)
print(f"\nDeleted task '{final.title}'")

# Final task count
print("\nFinal total tasks:", repo.count())
