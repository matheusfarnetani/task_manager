# Objective
Design and implement a CLI Task Manager on Python.

## Required features:
* Creating tasks with a title, description, to-do list and state
* Modifying and removing tasks
* Quickly marking tasks as "Done"
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
1. **Data model** & JSON schema
2. **Domain classes** (`Task`, `ToDoItem`) with basic behaviors
3. **Repository** (just JSON) and a quick smoke test of load/save
4. **GenericService** + **TaskService** unit tests (mock the repo)
5. **TaskManager** workflows (reorder, batch‑done) + tests
6. **CLI layer** wiring everything together


![[Architecture Overview.png]]

## JSON Schema
- **Complete Version:**

```json
{
  "guid": "e822ccac-0ddc-4251-826a-6e047099ccfe",
  "title": "Something",
  "description": "Or other",
  "responsible": "Matheus",
  "todo": [
    {
      "guid": "bcfb27f9-b0a7-4de5-9ec8-c10ca6637ba2",
      "text": "My first item",
      "done": false,
      "created_at": "2025-05-06T16:45:00Z",
      "completed_at": null
    },
    {
      "guid": "ca4a3dea-0e08-405c-a3f3-9188dc96db44",
      "text": "My second thing",
      "done": true,
      "created_at": "2025-05-05T09:20:00Z",
      "completed_at": "2025-05-05T12:00:00Z" 
    }
  ],
  "state": 2, // Enum(State, [("PENDING", 1), ("IN_PROGRESS", 2), ("DONE", 3)]),
  "deadline": "2025-05-08T16:00:00Z",
  "completed_at": "2025-05-08T16:00:00Z",
  "created_by": "Gaston",
  "created_at": "2025-05-06T16:00:00Z",
}
```

- **Simple Version:** (without relating to someone (personal usage))

```json
{
  "guid": "e822ccac-0ddc-4251-826a-6e047099ccfe",
  "title": "Something",
  "description": "Or other",
  "todo": [
    {
      "guid": "bcfb27f9-b0a7-4de5-9ec8-c10ca6637ba2",
      "text": "My first item",
      "done": false,
      "created_at": "2025-05-06T16:45:00Z",
      "completed_at": null
    },
    {
      "guid": "ca4a3dea-0e08-405c-a3f3-9188dc96db44",
      "text": "My second thing",
      "done": true,
      "created_at": "2025-05-05T09:20:00Z",
      "completed_at": "2025-05-05T12:00:00Z" 
    }
  ],
  "state": 2, // Enum(State, [("PENDING", 1), ("IN_PROGRESS", 2), ("DONE", 3)]),
  "deadline": "2025-05-08T16:00:00Z",
  "completed_at": "2025-05-08T16:00:00Z",
}
```

## Domain 
### Entities
#### `Task`

| Attribute    | Type               |
| ------------ | ------------------ |
| guid         | string             |
| title        | string             |
| description  | string or null     |
| todo         | `ToDoItem` or null |
| state        | int (default 1)    |
| deadline     | datetime           |
| completed_at | datetime or null   |

**Methods**
- `is_complete()`
	- `True` if state is `DONE` or all `ToDoItem` are done

#### `ToDoItem`
| Attribute    | Type                 |
| ------------ | -------------------- |
| guid         | string               |
| text         | string               |
| done         | bool (default false) |
| created_at   | datetime             |
| completed_at | datetime or null     |


## Persistence
### Data Storage
One single `.json` file

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
- **Loads** JSON file into memory and deserializes each record into a `Task` object
- **Writes** the full in‑memory list back to disk on every add, update, or delete
- **Handles** JSON ↔ domain mapping

### Auto‑save Strategy  
Component(s) at the service/manager layer track when data has changed and call the repository’s write methods immediately (or batch them, via a “dirty” flag) to persist updates without scattering I/O throughout your code.

## Business logic
1. `Task` has `Task_item`
2. `ToDoItem` only exists in a `Task`
3.  A `Task` or `ToDoItem` must be editable
4.  User can search a `Task`

### Relationships
`Task` perspective
- `Task` can or not have a `ToDoItem` (multiples)

`ToDoItem` perspective
- `ToDoItem` only exists inside of a tasks

### Services
#### `GenericService`
- CRUD

#### `TaskService`
- add, remove and modify `ToDoItem`
- reorder `ToDoItem`

### `TaskManager`
- Reorder `Tasks`
- Filter by title or GUID or state
