# Objective
Design and implement a CLI Task Manager on Python.

## Required features:
* Creating tasks with a title, description, to-do list and state
* Modifying and removing tasks
* Quickly marking tasks as `completed`
* Task filter

## Optional features:
* Auto-saving and loading to/from file
* Task re-ordering

## Questions:
* What structure would you use to store the tasks?
* How would you make the code easily extendable?


```python
from enum import Enum

class State(enum):
  PENDING = 1
  IN_PROGRESS = 2
  DONE = 3

{
  "title": "Something",
  "description": "Or other",
  "todo": [
    "My first item",
    "My second thing"
  ],
  "state": State.PENDING 
}
```

# Action plan:
1. **Define the data model** & JSON schema
2. **Implement domain classes** (`Task`, `ToDoItem`) with core behavior
3. **Implement the repository** (JSON-based) and test load/save
4. **Create services** (`GenericService`, `TaskService`) and unit test with mocked repo
5. **Build `TaskManager`** to manage workflows (reordering, batch-complete, etc.)
6. **Connect the CLI layer**, mapping user input to `TaskManager` methods

![Architecture Overview](Architecture%20Overview.png)

## JSON Schema
### Complete Version

```json
{
  "guid": "e822ccac-0ddc-4251-826a-6e047099ccfe",
  "title": "Something",
  "description": "Or other",
  "position": 1,
  "responsible": "Matheus",
  "todo": [
    {
      "guid": "bcfb27f9-b0a7-4de5-9ec8-c10ca6637ba2",
      "text": "My first item",
      "position": 1,
      "completed": false,
      "created_at": "2025-05-06T16:45:00Z",
      "completed_at": null
    },
    {
      "guid": "ca4a3dea-0e08-405c-a3f3-9188dc96db44",
      "text": "My second thing",
      "position": 2,
      "completed": true,
      "created_at": "2025-05-05T09:20:00Z",
      "completed_at": "2025-05-05T12:00:00Z" 
    }
  ],
  "state": 2,
  "deadline": "2025-05-08T16:00:00Z",
  "completed_at": "2025-05-08T16:00:00Z",
  "created_by": "Gaston",
  "created_at": "2025-05-06T16:00:00Z",
}
```
### Simple Version (for personal use)

```json
{
  "guid": "e822ccac-0ddc-4251-826a-6e047099ccfe",
  "title": "Something",
  "description": "Or other",
  "position": 1,
  "todo": [
    {
      "guid": "bcfb27f9-b0a7-4de5-9ec8-c10ca6637ba2",
      "text": "My first item",
      "position": 1,
      "completed": false,
      "created_at": "2025-05-06T16:45:00Z",
      "completed_at": null
    },
    {
      "guid": "ca4a3dea-0e08-405c-a3f3-9188dc96db44",
      "text": "My second thing",
      "position": 2,
      "completed": true,
      "created_at": "2025-05-05T09:20:00Z",
      "completed_at": "2025-05-05T12:00:00Z" 
    }
  ],
  "state": 2,
  "deadline": "2025-05-08T16:00:00Z",
  "completed_at": "2025-05-08T16:00:00Z",
}
```

## Domain
The Domain layer defines the objects that must exist in order to implement the program's behavior.
### Entities
#### `Task`
This is the main entity of the application. All service-layer functionality is designed to operate on this object.

| Attribute    | Type               |
| ------------ | ------------------ |
| guid         | string             |
| title        | string             |
| description  | string or null     |
| position     | int                |
| todo         | `ToDoItem` or null |
| state        | int (default 1)    |
| deadline     | datetime           |
| completed_at | datetime or null   |

**Methods**
- `is_complete()`
	- `True` if state is `COMPLETED` or all `ToDoItem` are completed

#### `ToDoItem`
The `ToDoItem` is an abstraction representing a checklist item required to complete a `Task`.

| Attribute    | Type                 |
| ------------ | -------------------- |
| guid         | string               |
| text         | string               |
| position     | int                  |
| completed    | bool (default false) |
| created_at   | datetime             |
| completed_at | datetime or null     |
### ID Strategy
Each `Task` and `ToDoItem` will have a globally unique identifier (UUID v4), generated automatically upon creation. This ensures that identifiers remain unique even if tasks are merged from different files or sources.

Example:
```python
import uuid
task_id = str(uuid.uuid4())
```

## Persistence
### Data Storage
All data will be stored in a single `.json` file.
Given the small scale of this CLI application, using a repository abstraction ensures a solid foundation for scalability. If the storage mechanism ever needs to change (e.g., from JSON to SQL), only the repository code needs to be updated.

### Repository Abstraction
Define an interface (`ITaskRepository`) with the core operations for decoupling storage from logic:
- `list_all() -> List[Task]`
- `get_by_guid(guid: str) -> Optional[Task]`
- `get_by_title(title: str) -> Optional[Task]`
- `get_by_state(state: State) -> Optional[Task]`
- `add(task: Task) -> None`
- `update(task: Task) -> None`
- `delete(guid: str) -> None`

### Concrete Implementation
- **Loads** the JSON file into memory and deserializes each record into a `Task` object
- **Writes** the entire list back to disk after each modification
- **Maps** between JSON and the domain model (e.g., `datetime`, `Enum`, etc.)

### Auto‑save Strategy  
Component(s) at the service and manager layer track when data has changed and call the repository’s write methods immediately (or batch them, via a “dirty” flag) to persist updates without scattering I/O.

## Business logic
1. `Task` contains multiple `ToDoItem`s (optional)
2.  A `ToDoItem` always belongs to a `Task`
3.  Both `Task` and `ToDoItem` must be editable
4.  User must be able to search and filter `Task`s

### Relationships
- From a `Task` perspective
	- A `Task` may have zero or more `ToDoItem`s

- From a `ToDoItem` perspective
	- A `ToDoItem` exists only as a part of a `Task`

### Services
#### `GenericService`
- Basic CRUD operations for any entity

#### `TaskService`
Responsible for all task-related operations. It builds upon `GenericService` and encapsulates the business logic related to `Task` and `ToDoItem`.

**Responsibilities:**
- Create, update, and delete tasks
- Reorder tasks by changing their position
- Add, remove, or reorder `ToDoItem`s within a task
- Mark an entire task or individual `ToDoItem`s as completed
- Set task state (`PENDING`, `IN_PROGRESS`, etc.)
- Count total tasks or total todos within a task
- Perform filtering queries, including:
    - By task state (`PENDING`, `IN_PROGRESS`, `COMPLETED`)
    - By title substring
    - By exact GUID
    - By deadline range (optional feature)

The `TaskService` is the main interface between the CLI layer and your application's core logic.

### Error Handling
- Task not found: 
	- Methods like `get_by_guid` or `get_by_title` could return `None`. The CLI should display a simple user-friendly message like "Task not found."
- **JSON file is malformed or missing**:  
	- On load, deserialization should be wrapped in a try-except block.
		- If it fails, the app will display an error and suggest file repair or recreation.

### State Transitions
Tasks have the following states:

```python
class State(enum.Enum):
    PENDING = 1
    IN_PROGRESS = 2
    COMPLETED = 3
```

Users can transition freely between states using the CLI, although the natural workflow is:
`PENDING → IN_PROGRESS → COMPLETED`.

Commands:
```bash
task set-state <guid> completed
```

### Position & Reordering
Every `Task` and `ToDoItem` includes a `position` field, which defines its order relative to sibling tasks or items in the list.
### Rules
- New items are inserted at the **end** of the list by default.
- Users can specify the position explicitly to insert items at a location.
- The system should validate and, if needed, reassign `position` values to:
	- Ensure uniqueness
	- Maintain contiguous order
	- Prevent collisions or gaps after reordering

Commands:
```bash
task move <guid> <new_position>
task todo move <task_guid> <item_guid> <new_position>
```

## CLI
The CLI is responsible for:
- Parsing terminal input and arguments
- Invoking service or manager methods
- Displaying output to the user

It does **not** manipulate data structures or JSON directly.  
Its only responsibility is to serve as the user-facing interface to the system.
The CLI will be implemented using the `argparse` module.

### Structure
The CLI will support the following commands:

```bash
task create --title "My Task" --description "Details"
task list [--state completed] [--title "filter"]
task view <guid>
task update <guid> [--title ...] [--description ...]
task complete <guid>
task delete <guid>
task set-state <guid> completed
task move <guid> <new_position>
task count

task todo add <task_guid> --text "My item"
task todo complete <task_guid> <item_guid>
task todo remove <task_guid> <item_guid>
task todo move <task_guid> <item_guid> <new_position>
task todo count <task_guid>
```

# Usage

## 1. Create a new `Task`

```bash
python3 main.py create --title "Test CLI Task" --description "Testing full CLI flow" --responsible "Tester" --deadline 2025-05-30
```

## 2. List all `Task`s

```bash
python3 main.py list
```

### Optional filters

```bash
# Filter by title substring
python3 main.py list --title "Test"

# Filter by state
python3 main.py list --state completed

# Filter tasks due in the next 3 days (default)
python3 main.py list --due-soon

# Filter tasks due in the next N days
python3 main.py list --due-soon 10

# Sort tasks by deadline or position
python3 main.py list --sort-by deadline
python3 main.py list --sort-by position

# Show output in raw JSON format
python3 main.py list --json
```

## 3. Filter `Task`s by `title` or `state`

```bash
python3 main.py list --title "Test"
python3 main.py list --state completed
```

## 4. View a `Task`

```bash
python3 main.py view <task_guid>
```

## 5. Update a `Task`

```bash
python3 main.py update <task_guid> --description "Updated desc" --responsible "Someone"
```

## 6. Set `Task`'s state manually

```bash
python3 main.py set-state <task_guid> in_progress
```

## 7. Mark `Task` as complete

```bash
python3 main.py complete <task_guid>
```

## 8. Move a `Task` to another position

```bash
python3 main.py move <task_guid> 2
```

## 9. Count all `Task`s

```bash
python3 main.py count
```

## 10. Add `ToDoItem`s

```bash
python3 main.py todo add <task_guid> --text "Step one"
python3 main.py todo add <task_guid> --text "Step two"
```

## 11. View updated `Task` with `ToDoItem`s

```bash
python3 main.py view <task_guid>
```

## 12. Update a `ToDoItem`

```bash
python3 main.py todo update <TASK_GUID> 2 --text "Revised step two" --position 1
```

## 13. Mark a `ToDoItem` as complete

```bash
python3 main.py todo complete <task_guid> 1
```

## 14. Move a `ToDoItem`

```bash
python3 main.py todo move <task_guid> 1 3
```

## 15. Count `ToDoItem`s

```bash
python3 main.py todo count <task_guid>
```

## 16. Remove a `ToDoItem`

```bash
python3 main.py todo remove <task_guid> 2
```

## 17. Delete a `Task`

```bash
python3 main.py delete <task_guid>
```
