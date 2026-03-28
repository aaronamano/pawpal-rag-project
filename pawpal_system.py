from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class TaskFrequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ONE_TIME = "one_time"


@dataclass
class Task:
    id: str
    title: str
    description: str
    frequency: TaskFrequency = TaskFrequency.DAILY
    priority: int = 1
    assigned_date: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    pet_id: str = ""
    notifications: list["Notification"] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def complete(self) -> None:
        """Mark the task as completed."""
        self.status = TaskStatus.COMPLETED

    def mark_pending(self) -> None:
        """Mark the task as pending."""
        self.status = TaskStatus.PENDING

    def is_overdue(self) -> bool:
        """Check if the task is past its assigned date and not completed."""
        if not self.assigned_date:
            return False
        if self.status == TaskStatus.COMPLETED:
            return False
        return datetime.now() > self.assigned_date

    def get_days_until_due(self) -> int:
        """Return the number of days until the task is due."""
        if not self.assigned_date:
            return -1
        delta = self.assigned_date - datetime.now()
        return delta.days

    def get_overdue_days(self) -> int:
        """Return the number of days the task is overdue."""
        if not self.is_overdue():
            return 0
        delta = datetime.now() - self.assigned_date
        return delta.days

    def add_notification(self, notification: "Notification") -> None:
        """Add a notification to the task."""
        self.notifications.append(notification)

    def __str__(self) -> str:
        status_icon = (
            "✓"
            if self.status == TaskStatus.COMPLETED
            else ("!" if self.is_overdue() else "○")
        )
        return f"[{status_icon}] {self.title} ({self.pet_id})"

    def __repr__(self) -> str:
        return (
            f"Task(id={self.id!r}, title={self.title!r}, status={self.status.value!r})"
        )


@dataclass
class Constraint:
    id: str
    title: str
    description: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    owner_id: str = ""

    def is_available(self, check_time: datetime) -> bool:
        """Check if the constraint is available at the given time."""
        if not self.start_time or not self.end_time:
            return True
        return not (self.start_time <= check_time <= self.end_time)

    def check_conflict(self, other: "Constraint") -> bool:
        """Check if this constraint conflicts with another constraint."""
        if not self.start_time or not other.start_time:
            return False
        return self.start_time <= other.end_time and other.start_time <= self.end_time

    def get_duration(self) -> int:
        """Return the duration of the constraint in minutes."""
        if not self.start_time or not self.end_time:
            return 0
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)


@dataclass
class Pet:
    id: str
    name: str
    animal: str
    breed: str = ""
    age: int = 0
    weight: float = 0.0
    tasks: list[Task] = field(default_factory=list)
    health_info: dict = field(default_factory=dict)
    owner_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def add_task(self, task: Task) -> None:
        """Add a task to the pet and set the task's pet_id."""
        task.pet_id = self.id
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the pet by its ID."""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                return True
        return False

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID."""
        return next((task for task in self.tasks if task.id == task_id), None)

    def get_pending_tasks(self) -> list[Task]:
        """Return all pending tasks for this pet."""
        return [task for task in self.tasks if task.status == TaskStatus.PENDING]

    def get_completed_tasks(self) -> list[Task]:
        """Return all completed tasks for this pet."""
        return [task for task in self.tasks if task.status == TaskStatus.COMPLETED]

    def get_overdue_tasks(self) -> list[Task]:
        """Return all overdue tasks for this pet."""
        return [task for task in self.tasks if task.is_overdue()]

    def get_tasks_by_status(self, status: TaskStatus) -> list[Task]:
        """Return all tasks with the given status."""
        return [task for task in self.tasks if task.status == status]

    def get_tasks_due_today(self) -> list[Task]:
        """Return all tasks due today."""
        today = datetime.now().date()
        return [
            task
            for task in self.tasks
            if task.assigned_date and task.assigned_date.date() == today
        ]

    def update_health_info(self, info: dict) -> None:
        """Update the pet's health information."""
        self.health_info.update(info)

    def get_task_count(self) -> dict[str, int]:
        """Return a dictionary with task counts by status."""
        return {
            "total": len(self.tasks),
            "pending": len(self.get_pending_tasks()),
            "completed": len(self.get_completed_tasks()),
            "overdue": len(self.get_overdue_tasks()),
        }

    def __str__(self) -> str:
        return f"{self.name} ({self.animal})"

    def __repr__(self) -> str:
        return f"Pet(id={self.id!r}, name={self.name!r}, animal={self.animal!r})"


@dataclass
class Owner:
    id: str
    name: str
    email: str = ""
    pets: list[Pet] = field(default_factory=list)
    constraints: list[Constraint] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)
    schedules: list["Schedule"] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner."""
        pet.owner_id = self.id
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> Optional[Pet]:
        """Remove a pet from the owner by its ID."""
        for i, pet in enumerate(self.pets):
            if pet.id == pet_id:
                return self.pets.pop(i)
        return None

    def get_pet_by_id(self, pet_id: str) -> Optional[Pet]:
        """Get a pet by its ID."""
        return next((pet for pet in self.pets if pet.id == pet_id), None)

    def add_constraint(self, constraint: Constraint) -> None:
        """Add a constraint to the owner."""
        constraint.owner_id = self.id
        self.constraints.append(constraint)

    def get_pets(self) -> list[Pet]:
        """Return all pets owned by this owner."""
        return self.pets

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks for all pets owned by this owner."""
        return [task for pet in self.pets for task in pet.tasks]

    def get_all_pending_tasks(self) -> list[Task]:
        """Return all pending tasks for all pets owned by this owner."""
        return [task for pet in self.pets for task in pet.get_pending_tasks()]

    def get_all_overdue_tasks(self) -> list[Task]:
        """Return all overdue tasks for all pets owned by this owner."""
        return [task for pet in self.pets for task in pet.get_overdue_tasks()]

    def update_preferences(self, prefs: dict) -> None:
        """Update the owner's preferences."""
        self.preferences.update(prefs)

    def add_schedule(self, schedule: "Schedule") -> None:
        """Add a schedule to the owner."""
        self.schedules.append(schedule)

    def get_pet_count(self) -> int:
        """Return the number of pets owned by this owner."""
        return len(self.pets)

    def get_total_task_count(self) -> dict[str, int]:
        """Return a dictionary with total task counts across all pets."""
        total = {"total": 0, "pending": 0, "completed": 0, "overdue": 0}
        for pet in self.pets:
            counts = pet.get_task_count()
            for key in total:
                total[key] += counts[key]
        return total

    def __str__(self) -> str:
        return f"{self.name} ({len(self.pets)} pets)"


@dataclass
class Notification:
    id: str
    message: str
    scheduled_time: Optional[datetime] = None
    task: Optional[Task] = None
    is_sent: bool = False

    def send(self) -> None:
        """Send the notification and mark it as sent."""
        self.is_sent = True
        print(f"Notification [{self.id}]: {self.message}")

    def reschedule(self, new_time: datetime) -> None:
        """Reschedule the notification to a new time."""
        self.scheduled_time = new_time
        self.is_sent = False

    def __str__(self) -> str:
        status = "sent" if self.is_sent else "pending"
        return f"Notification: {self.message} ({status})"


@dataclass
class Schedule:
    id: str
    date: datetime
    owner: Optional[Owner] = None
    scheduled_tasks: list[Task] = field(default_factory=list)

    def generate_schedule(self, include_completed: bool = False) -> list[Task]:
        """Generate a schedule of tasks for the owner, sorted by priority."""
        if not self.owner:
            return []

        all_tasks = [pet.tasks for pet in self.owner.pets]
        tasks = [task for sublist in all_tasks for task in sublist]

        if not include_completed:
            tasks = [t for t in tasks if t.status != TaskStatus.COMPLETED]

        tasks.sort(
            key=lambda t: (t.priority, t.assigned_date or datetime.min), reverse=True
        )
        return tasks

    def add_task_to_schedule(self, task: Task) -> None:
        """Add a task to the schedule."""
        if task not in self.scheduled_tasks:
            self.scheduled_tasks.append(task)

    def remove_task_from_schedule(self, task_id: str) -> bool:
        """Remove a task from the schedule by its ID."""
        for i, task in enumerate(self.scheduled_tasks):
            if task.id == task_id:
                self.scheduled_tasks.pop(i)
                return True
        return False

    def get_daily_tasks(self) -> list[Task]:
        """Return all tasks scheduled for the schedule's date."""
        return [
            t
            for t in self.scheduled_tasks
            if t.assigned_date and t.assigned_date.date() == self.date.date()
        ]

    def get_pending_daily_tasks(self) -> list[Task]:
        """Return all pending tasks scheduled for the schedule's date."""
        return [t for t in self.get_daily_tasks() if t.status == TaskStatus.PENDING]


@dataclass
class Scheduler:
    owners: dict[str, Owner] = field(default_factory=dict)
    pet_index: dict[str, Pet] = field(default_factory=dict)
    task_index: dict[str, Task] = field(default_factory=dict)
    schedules: list["Schedule"] = field(default_factory=list)

    def register_owner(self, owner: Owner) -> None:
        """Register an owner and all their pets with the scheduler."""
        self.owners[owner.id] = owner
        for pet in owner.pets:
            self.register_pet(pet)

    def register_pet(self, pet: Pet) -> None:
        """Register a pet and all its tasks with the scheduler."""
        self.pet_index[pet.id] = pet
        for task in pet.tasks:
            self.register_task(task)

    def register_task(self, task: Task) -> None:
        """Register a task with the scheduler."""
        self.task_index[task.id] = task

    def get_owner_by_id(self, owner_id: str) -> Optional[Owner]:
        """Get an owner by their ID."""
        return self.owners.get(owner_id)

    def get_pet_by_id(self, pet_id: str) -> Optional[Pet]:
        """Get a pet by its ID."""
        return self.pet_index.get(pet_id)

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID."""
        return self.task_index.get(task_id)

    def get_all_owners(self) -> list[Owner]:
        """Return all registered owners."""
        return list(self.owners.values())

    def get_all_pets(self) -> list[Pet]:
        """Return all registered pets."""
        return list(self.pet_index.values())

    def get_all_tasks(self) -> list[Task]:
        """Return all registered tasks."""
        return list(self.task_index.values())

    def get_all_pending_tasks(self) -> list[Task]:
        """Return all pending tasks across the system."""
        return [t for t in self.task_index.values() if t.status == TaskStatus.PENDING]

    def get_all_overdue_tasks(self) -> list[Task]:
        """Return all overdue tasks across the system."""
        return [t for t in self.task_index.values() if t.is_overdue()]

    def get_tasks_by_pet(self, pet_id: str) -> list[Task]:
        """Return all tasks for a specific pet."""
        pet = self.pet_index.get(pet_id)
        return pet.tasks if pet else []

    def get_tasks_by_owner(self, owner_id: str) -> list[Task]:
        """Return all tasks for a specific owner."""
        owner = self.owners.get(owner_id)
        return owner.get_all_tasks() if owner else []

    def get_tasks_due_today(self) -> list[Task]:
        """Return all tasks due today across the system."""
        today = datetime.now().date()
        return [
            t
            for t in self.task_index.values()
            if t.assigned_date and t.assigned_date.date() == today
        ]

    def get_tasks_due_soon(self, days: int = 3) -> list[Task]:
        """Return all tasks due within the specified number of days."""
        soon = datetime.now() + timedelta(days=days)
        return [
            t
            for t in self.task_index.values()
            if t.assigned_date
            and TaskStatus.PENDING
            and datetime.now() <= t.assigned_date <= soon
        ]

    def get_tasks_by_priority(self, min_priority: int = 1) -> list[Task]:
        """Return all tasks with priority >= min_priority, sorted by priority."""
        return sorted(
            [t for t in self.task_index.values() if t.priority >= min_priority],
            key=lambda t: t.priority,
            reverse=True,
        )

    def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed by its ID."""
        task = self.task_index.get(task_id)
        if task:
            task.complete()
            return True
        return False

    def remove_pet(self, pet_id: str) -> bool:
        """Remove a pet and all its tasks from the scheduler."""
        if pet_id in self.pet_index:
            pet = self.pet_index.pop(pet_id)
            for task in pet.tasks:
                self.task_index.pop(task.id, None)
            return True
        return False

    def remove_owner(self, owner_id: str) -> bool:
        """Remove an owner and all their pets from the scheduler."""
        if owner_id in self.owners:
            owner = self.owners.pop(owner_id)
            for pet in owner.pets:
                self.remove_pet(pet.id)
            return True
        return False

    def generate_schedule(
        self, owner_id: str, date: Optional[datetime] = None
    ) -> "Schedule":
        """Generate a schedule for an owner on the given date."""
        schedule = Schedule(
            id=f"schedule_{len(self.schedules) + 1}",
            date=date or datetime.now(),
            owner=self.owners.get(owner_id),
        )
        self.schedules.append(schedule)
        return schedule

    def get_system_stats(self) -> dict:
        """Return statistics about the system."""
        all_tasks = self.get_all_tasks()
        return {
            "total_owners": len(self.owners),
            "total_pets": len(self.pet_index),
            "total_tasks": len(all_tasks),
            "pending_tasks": len(
                [t for t in all_tasks if t.status == TaskStatus.PENDING]
            ),
            "completed_tasks": len(
                [t for t in all_tasks if t.status == TaskStatus.COMPLETED]
            ),
            "overdue_tasks": len(self.get_all_overdue_tasks()),
        }
