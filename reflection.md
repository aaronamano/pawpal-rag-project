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
        +List~Task~ scheduledTasks
        +generateSchedule(owner: Owner): List~Task~
        +addTaskToSchedule(task: Task): void
        +removeTaskFromSchedule(taskId: String): void
        +getDailyTasks(): List~Task~
    }
    class Notification {
        +String id
        +String message
        +DateTime scheduledTime
        +String taskId
        +send(): void
        +reschedule(newTime: DateTime): void
    }
    Owner "1" --> "*" Pet : manages
    Owner "1" --> "*" Constraint : has
    Pet "1" --> "*" Task : assigned
    Schedule "1" --> "*" Task : contains
    Task "1" --> "*" Notification : triggers
```

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
