from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    id: str
    title: str
    description: str
    frequency: str = "daily"
    priority: int = 1
    assigned_date: Optional[datetime] = None
    status: str = "pending"
    pet_id: str = ""

    def complete(self) -> None:
        self.status = "completed"

    def mark_pending(self) -> None:
        self.status = "pending"

    def is_overdue(self) -> bool:
        if not self.assigned_date:
            return False
        return datetime.now() > self.assigned_date and self.status == "pending"

    def get_days_until_due(self) -> int:
        if not self.assigned_date:
            return -1
        delta = self.assigned_date - datetime.now()
        return delta.days


@dataclass
class Constraint:
    id: str
    title: str
    description: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    owner_id: str = ""

    def is_available(self, check_time: datetime) -> bool:
        if not self.start_time or not self.end_time:
            return True
        return not (self.start_time <= check_time <= self.end_time)

    def check_conflict(self, other: "Constraint") -> bool:
        if not self.start_time or not other.start_time:
            return False
        return self.start_time <= other.end_time and other.start_time <= self.end_time

    def get_duration(self) -> int:
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

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> bool:
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks.pop(i)
                return True
        return False

    def get_pending_tasks(self) -> list[Task]:
        return [task for task in self.tasks if task.status == "pending"]

    def update_health_info(self, info: dict) -> None:
        self.health_info.update(info)


@dataclass
class Owner:
    id: str
    name: str
    email: str = ""
    pets: list[Pet] = field(default_factory=list)
    constraints: list[Constraint] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> bool:
        for i, pet in enumerate(self.pets):
            if pet.id == pet_id:
                self.pets.pop(i)
                return True
        return False

    def add_constraint(self, constraint: Constraint) -> None:
        self.constraints.append(constraint)

    def get_pets(self) -> list[Pet]:
        return self.pets

    def update_preferences(self, prefs: dict) -> None:
        self.preferences.update(prefs)


@dataclass
class Notification:
    id: str
    message: str
    scheduled_time: Optional[datetime] = None
    task_id: str = ""

    def send(self) -> None:
        print(f"Notification: {self.message}")

    def reschedule(self, new_time: datetime) -> None:
        self.scheduled_time = new_time


@dataclass
class Schedule:
    id: str
    date: datetime
    scheduled_tasks: list[Task] = field(default_factory=list)

    def generate_schedule(self, owner: Owner) -> list[Task]:
        all_tasks = []
        for pet in owner.pets:
            all_tasks.extend(pet.tasks)
        all_tasks.sort(key=lambda t: (t.priority, t.assigned_date or datetime.min))
        return all_tasks

    def add_task_to_schedule(self, task: Task) -> None:
        self.scheduled_tasks.append(task)

    def remove_task_from_schedule(self, task_id: str) -> bool:
        for i, task in enumerate(self.scheduled_tasks):
            if task.id == task_id:
                self.scheduled_tasks.pop(i)
                return True
        return False

    def get_daily_tasks(self) -> list[Task]:
        return [
            t
            for t in self.scheduled_tasks
            if t.assigned_date and t.assigned_date.date() == self.date.date()
        ]
