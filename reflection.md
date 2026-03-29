# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

actions:

1. enter a pet and input its attributes; assign the pet tasks
2. add constraints such as availability, priority, and owner preferences
3. schedule a plan for the pets

class Pet:
name -> String
animal -> String (e.g. dog, cat, etc.)
tasks -> [Task]

class Task:
title -> String
description -> String

class Constraint:
title -> String
description -> String
availability -> datetime

class Owner:
name -> String
pets -> [Pet]
constraints -> [Constraint]

Mermaid JS diagram

```js
classDiagram
    class Owner {
        +String id
        +String name
        +String email
        +List~Pet~ pets
        +List~Constraint~ constraints
        +Dict preferences
        +addPet(pet: Pet): void
        +removePet(petId: String): void
        +addConstraint(constraint: Constraint): void
        +getPets(): List~Pet~
        +updatePreferences(prefs: Dict): void
    }
    class Pet {
        +String id
        +String name
        +String animal
        +String breed
        +int age
        +float weight
        +List~Task~ tasks
        +Dict healthInfo
        +addTask(task: Task): void
        +removeTask(taskId: String): void
        +getPendingTasks(): List~Task~
        +updateHealthInfo(info: Dict): void
    }
    class Task {
        +String id
        +String title
        +String description
        +String frequency
        +int priority
        +DateTime assignedDate
        +String status
        +String petId
        +complete(): void
        +markPending(): void
        +isOverdue(): boolean
        +getDaysUntilDue(): int
    }
    class Constraint {
        +String id
        +String title
        +String description
        +DateTime startTime
        +DateTime endTime
        +String ownerId
        +isAvailable(dateTime: DateTime): boolean
        +checkConflict(other: Constraint): boolean
        +getDuration(): int
    }
    class Schedule {
        +String id
        +DateTime date
        +Owner owner
        +List~Task~ scheduledTasks
        +generateSchedule(): List~Task~
        +addTaskToSchedule(task: Task): void
        +removeTaskFromSchedule(taskId: String): void
        +getDailyTasks(): List~Task~
    }
    class Notification {
        +String id
        +String message
        +DateTime scheduledTime
        +Task task
        +send(): void
        +reschedule(newTime: DateTime): void
    }
    class PetManager {
        +Dict~String, Pet~ petIndex
        +Dict~String, Task~ taskIndex
        +getPetById(id: String): Pet
        +getTaskById(id: String): Task
        +getAllTasks(): List~Task~
    }
    Owner "1" --> "*" Pet : manages
    Owner "1" --> "*" Constraint : has
    Owner "1" --> "*" Schedule : owns
    Pet "1" --> "*" Task : assigned
    Schedule "1" --> "1" Owner : belongs to
    Schedule "1" --> "*" Task : contains
    Task "1" --> "*" Notification : triggers
    PetManager ..> Pet : indexes
    PetManager ..> Task : indexes
```

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

```text
Missing Relationships
Issue -> Problem
Owner → Schedule -> Schedule.generate_schedule(owner) needs a relationship, but none exists. A Schedule should belong to an Owner.
Notification → Task/Schedule -> Notification has taskId but no explicit link. The "triggers" relationship is shown backwards (should be Notification linked TO Task).
Bidirectional Pet↔Task -> Task has petId, Pet has tasks list, but no explicit back-reference relationship shown.

Bottlenecks
Issue -> Problem
Schedule.generate_schedule() -> Pulls ALL tasks from ALL pets every time. O(n) traversal with no caching. Scales poorly with many pets/tasks.
Pet.tasks list	-> No pagination or filtering built-in. get_pending_tasks() still scans entire list.
No indexing	-> All lookups by id are linear O(n) scans.

Suggested Fixes
1. Add Owner "1" --> "*" Schedule relationship
2. Make Schedule store a reference to its owner
3. Consider adding a TaskRepository or PetManager class to centralize lookups and add indexing
```

```text
Done. Updates:
reflection.md UML:
- Added PetManager class with indexing methods
- Schedule now has Owner reference and generateSchedule() uses it directly
- Notification links to Task directly
- Added Owner "1" --> "*" Schedule relationship
- Fixed notification relationship direction
pawpal_system.py:
- Added PetManager with O(1) lookups by pet_id and task_id
- Schedule.generate_schedule() now uses its owner attribute instead of parameter
- Added Owner.schedules list and add_schedule() method
- Added Task.notifications list and add_notification() method
- PetManager.register_pet() auto-indexes pet's tasks
```

initially there was no relationship between the owner and the schedule which made it difficult to see which schedule is which. i allowed the coding agent to enable a relationship between the owner and the schedule so the schedule has a owner id assigned to it.

also there was a bottleneck where tasks are retrieved in O(n) time which is potentially inefficient since ALL of tasks are retrieved given there was no identifiers originally to handle this bottleneck, so i let the coding agent assign unique ids like task_id and pet_id to retrieve tasks quicker in constant time instead of retrieving ALL of them from ALL users and pets.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  The generate_schedule method has repetetitive lambda patterns and multiple if/elif branches to try to sort tasks whether it's by priority, date, status, or pet name.

However, the AI coding agent proposed creating a dictionary mapping to sort tasks more efficiently by searching the keyword quickly: "priority", "date", "status", or "pet name" due to its constant time lookup and we can eliminate the if/elif/else chain. we would use the lambda sorting method as the value and the filter word as the key.

```python
sort_keys = {
        "priority": lambda t: (-t.priority, date_key(t)),
        "date": lambda t: (date_key(t), -t.priority),
        "pet_name": lambda t: (
            pet_names.get(t.pet_id, "").lower(),
            -t.priority,
            date_key(t),
        ),
        "status": lambda t: (t.status.value, -t.priority, date_key(t)),
    }
```

- Why is that tradeoff reasonable for this scenario?
The new tradeoff the AI coding agent proposed was reasonable and better becuase the code looked cleaner and still adhered to the logic. Additionally, the sorting method by keyword was efficient with the quick, constant time lookup

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
