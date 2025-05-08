# task_manager/cli/cli.py

import argparse
from datetime import datetime
from task_manager.domain.state import State
from task_manager.domain.todo_item import ToDoItem
from task_manager.domain.task import Task
from task_manager.repository.json_repo import JsonTaskRepository
from task_manager.services.task_service import TaskService


def run_cli():
    parser = argparse.ArgumentParser(
        description="Task Manager CLI",
        epilog="""
Examples:
  task create --title "Buy milk" --deadline 2025-05-10
  task list --state completed
  task view <guid>
  task todo add <guid> --text "Call the doctor"
"""
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Task commands
    # Create Task
    create_parser = subparsers.add_parser("create", help="Create a new task")
    create_parser.add_argument(
        "--title", required=True, help="Title of the task")
    create_parser.add_argument(
        "--description", help="Optional task description")
    create_parser.add_argument(
        "--responsible", help="Person responsible for the task")
    create_parser.add_argument(
        "--state",
        default="PENDING",
        choices=[s.name for s in State],
        type=str.upper,
        help="Initial task state."
    )
    create_parser.add_argument(
        "--deadline", required=True, help="Deadline (format: YYYY-MM-DD)")
    create_parser.add_argument(
        "--json", action="store_true", help="Show raw JSON output")

    # List and filter Tasks
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument(
        "--state",
        default="PENDING",
        choices=[s.name for s in State],
        type=str.upper,
        help="Initial task state."
    )
    list_parser.add_argument(
        "--title", help="Filter by title (case-insensitive substring)")
    list_parser.add_argument("--due-soon", nargs="?", const=3, type=int,
                             help="Filter tasks due in the next N days (default: 3 if no value is provided)")
    list_parser.add_argument(
        "--sort-by", choices=["position", "deadline"], help="Sort tasks by the given field")
    list_parser.add_argument(
        "--json", action="store_true", help="Print output in JSON format")

    # View Task
    view_parser = subparsers.add_parser("view", help="View a task")
    view_parser.add_argument("guid", help="GUID of the task to view")
    view_parser.add_argument(
        "--json", action="store_true", help="Show raw JSON output")

    # Update Task
    update_parser = subparsers.add_parser("update", help="Update task fields")
    update_parser.add_argument("guid", help="GUID of the task to update")
    update_parser.add_argument("--title", help="New title")
    update_parser.add_argument("--description", help="New description")
    update_parser.add_argument("--responsible", help="New responsible person")
    update_parser.add_argument(
        "--position", type=int, help="New position in the list")
    update_parser.add_argument(
        "--state",
        default="PENDING",
        choices=[s.name for s in State],
        type=str.upper,
        help="Initial task state."
    )
    update_parser.add_argument(
        "--deadline", help="New deadline (format: YYYY-MM-DD)")
    update_parser.add_argument("--created_by", help="New creator name")
    update_parser.add_argument(
        "--json", action="store_true", help="Show raw JSON output")

    # Count Tasks
    subparsers.add_parser("count", help="Total number of tasks")

    # Complete Task
    complete_parser = subparsers.add_parser(
        "complete", help="Mark task as complete")
    complete_parser.add_argument("guid")
    complete_parser.add_argument(
        "--json", action="store_true", help="Show raw JSON output")

    # Set-state of a Task
    state_parser = subparsers.add_parser("set-state", help="Change task state")
    state_parser.add_argument("guid")
    state_parser.add_argument("state")

    # Move a Task
    move_parser = subparsers.add_parser(
        "move", help="Move task to new position")
    move_parser.add_argument("guid")
    move_parser.add_argument("new_position", type=int)

    # Delete a Task
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("guid")

    # ToDo commands
    todo = subparsers.add_parser("todo", help="Manage todos")
    todo_sub = todo.add_subparsers(dest="todo_cmd", required=True)

    # Add ToDo
    todo_add = todo_sub.add_parser("add", help="Add a new ToDo to a task")
    todo_add.add_argument(
        "task_guid", help="GUID of the task to add the ToDo to")
    todo_add.add_argument("--text", required=True,
                          help="Text content of the new ToDo item")

    # Update ToDo
    todo_update = todo_sub.add_parser(
        "update", help="Update a ToDo item by position")
    todo_update.add_argument(
        "task_guid", help="GUID of the task containing the ToDo")
    todo_update.add_argument("item_position", type=int,
                             help="Current position of the ToDo")
    todo_update.add_argument("--text", help="New text for the ToDo")
    todo_update.add_argument("--position", type=int,
                             help="New position within the task")

    # Complete ToDo
    todo_complete = todo_sub.add_parser(
        "complete", help="Mark a ToDo item as completed (by position)")
    todo_complete.add_argument(
        "task_guid", help="GUID of the task containing the ToDo")
    todo_complete.add_argument(
        "item_position", type=int, help="Position of the ToDo to complete")

    # Delete ToDo
    todo_remove = todo_sub.add_parser(
        "remove", help="Remove a ToDo item from a task (by position)")
    todo_remove.add_argument("task_guid", help="GUID of the task")
    todo_remove.add_argument("item_position", type=int,
                             help="Position of the ToDo to remove")

    # Move ToDo
    todo_move = todo_sub.add_parser(
        "move", help="Reorder a ToDo item within a task")
    todo_move.add_argument("task_guid", help="GUID of the task")
    todo_move.add_argument("item_position", type=int,
                           help="Current position of the ToDo")
    todo_move.add_argument("new_position", type=int,
                           help="Target position for the ToDo")

    # Count ToDo
    todo_count = todo_sub.add_parser(
        "count", help="Count the number of ToDo items in a task")
    todo_count.add_argument(
        "task_guid", help="GUID of the task to count ToDo items for")

    args = parser.parse_args()

    # Repo + Service Init
    repo = JsonTaskRepository("tasks.json")
    service = TaskService(repo)

    # Handle Commands
    if args.command == "create":
        deadline = datetime.fromisoformat(args.deadline)
        state = State[args.state.upper()]
        task = Task.create(
            title=args.title,
            position=repo.count() + 1,
            state=state,
            deadline=deadline,
            created_by="cli",
            responsible=args.responsible,
            description=args.description,
        )
        service.create(task)
        if args.json:
            print(service.to_json([task]))
        else:
            print(f"Created task: {task.title} (GUID: {task.guid})")

    elif args.command == "list":
        if args.due_soon is not None:
            tasks = service.filter_due_soon(days=args.due_soon)
        else:
            tasks = service.get_all()

        if args.state:
            tasks = service.filter_by_state(State[args.state], tasks)
        if args.title:
            tasks = service.filter_by_title(args.title, tasks)

        if args.sort_by:
            tasks = service.sort_tasks(tasks, args.sort_by)

        if args.json:
            print(service.to_json(tasks))
        else:
            for t in tasks:
                print(f"- {t.title} ({t.state.name}) | GUID: {t.guid}")

    elif args.command == "view":
        task = service.get_by_guid(args.guid)
        if not task:
            print("Task not found.")
        elif args.json:
            print(service.to_json([task]))
        else:
            print(task)

    elif args.command == "update":
        updates = {k: v for k, v in vars(args).items() if k not in (
            "guid", "command") and v is not None}

        if "state" in updates:
            updates["state"] = State[updates["state"].upper()]
        if "deadline" in updates:
            updates["deadline"] = datetime.fromisoformat(updates["deadline"])

        service.update_task(args.guid, **updates)
        if args.json:
            print(service.to_json([task]))
        else:
            print(f"Task {args.guid} updated.")

    elif args.command == "count":
        print(f"Total tasks: {service.count()}")

    elif args.command == "complete":
        service.mark_task_complete(args.guid)
        if args.json:
            print(service.to_json([task]))
        else:
            print(f"Task {args.guid} marked as complete.")

    elif args.command == "set-state":
        service.set_state(args.guid, State[args.state.upper()])
        print(f"Task {args.guid} state set to {args.state.upper()}.")

    elif args.command == "move":
        service.move_task(args.guid, args.new_position)
        print(f"Task {args.guid} moved to position {args.new_position}.")

    elif args.command == "delete":
        service.delete(args.guid)
        print(f"Task {args.guid} deleted.")

    # ToDo Commands
    elif args.command == "todo":
        if args.todo_cmd == "add":
            item = ToDoItem.create(args.text)
            service.add_todo(args.task_guid, item)
            print(f"Added ToDo to task {args.task_guid}")

        elif args.todo_cmd == "update":
            item = service.get_by_guid(
                args.task_guid).get_todo_by_position(args.item_position)
            if args.text:
                item.text = args.text
            if args.position and args.position != item.position:
                service.reorder_todo(
                    args.task_guid, item.position, args.position)
            service.update(service.get_by_guid(args.task_guid))  # Save changes
            print(f"Updated ToDo at position {args.item_position}")

        elif args.todo_cmd == "complete":
            service.mark_todo_complete(args.task_guid, int(args.item_position))
            print(f"Marked ToDo {args.item_position} as complete.")

        elif args.todo_cmd == "remove":
            service.remove_todo(args.task_guid, int(args.item_position))
            print(
                f"Removed ToDo {args.item_position} from task {args.task_guid}")

        elif args.todo_cmd == "move":
            service.reorder_todo(args.task_guid, int(
                args.item_position), args.new_position)
            print(f"Moved ToDo to position {args.new_position}")

        elif args.todo_cmd == "count":
            count = service.get_todo_count(args.task_guid)
            print(f"Task {args.task_guid} has {count} ToDo items")
