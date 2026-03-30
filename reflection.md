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
    class TaskStatus {
        <<enumeration>>
        PENDING
        COMPLETED
        OVERDUE
        CANCELLED
    }
    class TaskFrequency {
        <<enumeration>>
        DAILY
        WEEKLY
        MONTHLY
        ONE_TIME
    }
    class Owner {
        +String id
        +String name
        +String email
        +List~Pet~ pets
        +List~Constraint~ constraints
        +Dict preferences
        +List~Schedule~ schedules
        +DateTime createdAt
        +addPet(pet: Pet): void
        +removePet(petId: String): Pet
        +getPetById(petId: String): Pet
        +addConstraint(constraint: Constraint): void
        +getPets(): List~Pet~
        +getAllTasks(): List~Task~
        +getAllPendingTasks(): List~Task~
        +getAllOverdueTasks(): List~Task~
        +updatePreferences(prefs: Dict): void
        +addSchedule(schedule: Schedule): void
        +getPetCount(): int
        +getTotalTaskCount(): Dict
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
        +String ownerId
        +DateTime createdAt
        +addTask(task: Task): void
        +removeTask(taskId: String): boolean
        +getTaskById(taskId: String): Task
        +getPendingTasks(): List~Task~
        +getCompletedTasks(): List~Task~
        +getOverdueTasks(): List~Task~
        +getTasksByStatus(status: TaskStatus): List~Task~
        +getTasksDueToday(): List~Task~
        +updateHealthInfo(info: Dict): void
        +getTaskCount(): Dict
    }
    class Task {
        +String id
        +String title
        +String description
        +TaskFrequency frequency
        +int priority
        +DateTime assignedDate
        +TaskStatus status
        +String petId
        +List~Notification~ notifications
        +DateTime createdAt
        +complete(): void
        +markPending(): void
        +isOverdue(): boolean
        +getDaysUntilDue(): int
        +getOverdueDays(): int
        +addNotification(notification: Notification): void
    }
    class Constraint {
        +String id
        +String title
        +String description
        +DateTime startTime
        +DateTime endTime
        +String ownerId
        +isAvailable(checkTime: DateTime): boolean
        +checkConflict(other: Constraint): boolean
        +getDuration(): int
    }
    class Schedule {
        +String id
        +DateTime date
        +Owner owner
        +List~Task~ scheduledTasks
        +generateSchedule(includeCompleted, sortBy, filterStatus): List~Task~
        +addTaskToSchedule(task: Task): void
        +removeTaskFromSchedule(taskId: String): boolean
        +getDailyTasks(): List~Task~
        +getPendingDailyTasks(): List~Task~
    }
    class Notification {
        +String id
        +String message
        +DateTime scheduledTime
        +Task task
        +boolean isSent
        +send(): void
        +reschedule(newTime: DateTime): void
    }
    class Scheduler {
        +Dict~String, Owner~ owners
        +Dict~String, Pet~ petIndex
        +Dict~String, Task~ taskIndex
        +List~Schedule~ schedules
        +registerOwner(owner: Owner): void
        +registerPet(pet: Pet): void
        +registerTask(task: Task): void
        +getOwnerById(ownerId: String): Owner
        +getPetById(petId: String): Pet
        +getTaskById(taskId: String): Task
        +getAllOwners(): List~Owner~
        +getAllPets(): List~Pet~
        +getAllTasks(): List~Task~
        +getAllPendingTasks(): List~Task~
        +getAllOverdueTasks(): List~Task~
        +getTasksByPet(petId: String): List~Task~
        +getTasksByOwner(ownerId: String): List~Task~
        +getTasksDueToday(): List~Task~
        +getTasksDueSoon(days: int): List~Task~
        +getTasksByPriority(minPriority: int): List~Task~
        +detectConflicts(petId: String): List~Tuple~
        +checkConflictsWarning(petId: String): String
        +completeTask(taskId: String): Task
        +removePet(petId: String): boolean
        +removeOwner(ownerId: String): boolean
        +generateSchedule(ownerId: String, date: DateTime): Schedule
        +getSystemStats(): Dict
    }
    Owner "1" --> "*" Pet : manages
    Owner "1" --> "*" Constraint : has
    Owner "1" --> "*" Schedule : owns
    Pet "1" --> "*" Task : assigned
    Pet "1" --> "1" Owner : belongs to
    Schedule "1" --> "1" Owner : belongs to
    Schedule "1" --> "*" Task : contains
    Task "1" --> "1" Pet : belongs to
    Task "1" --> "*" Notification : triggers
    Notification "*" --> "1" Task : for
    Scheduler "1" --> "*" Owner : manages
    Scheduler "1" --> "*" Pet : indexes
    Scheduler "1" --> "*" Task : indexes
    Scheduler "1" --> "*" Schedule : manages
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

The constraints my scheduler considered was priority, urgency, and date.
I decided which constraints mattered most based off personal experience whenever I have a lot of tasks to do and reflect on what tasks I need to prioritize.

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

I used AI tools to be able to design the UML diagram, implement the object classes from the diagram, create test cases, and update the UI of the app.
The prompt that was the most helpful was to ask the AI tool to create and design tests solely for edge cases.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

I tried to ask AI why data doesn't persist while I refresh it, and afterwards it suggested a sqlite or local json database to ensure data persists via querying it.

I decided what the AI suggested by asking myself how the outcome would turn out if we implemented x and if it is worth it as well as how much it can impact our codebase/system.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested various behaviors where we had to sort tasks based on different filters and handle recurring tasks. I also tested behaviors where we add a task and see if the number of tasks had updated for a certain pet and ensuring that certain tasks were completed if we checked them off.

These tests were important because they would help the user manage tasks more efficiently and focus on the ones they need to do.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am pretty confident my scheduler works correctly since we implemented tests that the AI worked on based on the system it implemented for the UI.

At the moment, I don't think there are many edge cases I would like to test next time. I would probably work on sorting tasks by pet name, accounting for an edge case where multiple pets might have the same name.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

the part i am satisfied with is that the system it implemented passed test cases and directly worked with the UI

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

i would improve handling features where users can edit the tasks and/or information of pet names they created.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

i learned that designing a system architecture is crucial and that you need to account for edge cases and seeing if the system as the whole works through testing. also breaking an system down into components to understand the entire functionality can be helpful.
