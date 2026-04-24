import json
from datetime import datetime
from typing import Optional, Any
from pawpal_system import (
    Task,
    Pet,
    Owner,
    Scheduler,
    TaskStatus,
    TaskFrequency,
    Schedule,
)


class DataStorage:
    def __init__(self, filepath: str = "pawpal_data.json"):
        self.filepath = filepath

    def _load_data(self) -> dict:
        try:
            with open(self.filepath, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"owners": [], "scheduler": {}}

    def _save_data(self, data: dict) -> None:
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2, default=self._json_serializer)

    def _json_serializer(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return str(obj)

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        if dt_str:
            try:
                return datetime.fromisoformat(dt_str)
            except (ValueError, TypeError):
                return None
        return None

    def _dict_to_task(self, task_dict: dict) -> Task:
        return Task(
            id=task_dict.get("id", ""),
            title=task_dict.get("title", ""),
            description=task_dict.get("description", ""),
            frequency=TaskFrequency(task_dict.get("frequency", "one_time")),
            priority=task_dict.get("priority", 1),
            assigned_date=self._parse_datetime(task_dict.get("assigned_date")),
            status=TaskStatus(task_dict.get("status", "pending")),
            pet_id=task_dict.get("pet_id", ""),
            created_at=self._parse_datetime(task_dict.get("created_at"))
            or datetime.now(),
        )

    def _task_to_dict(self, task: Task) -> dict:
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "frequency": task.frequency.value,
            "priority": task.priority,
            "assigned_date": task.assigned_date.isoformat()
            if task.assigned_date
            else None,
            "status": task.status.value,
            "pet_id": task.pet_id,
            "created_at": task.created_at.isoformat() if task.created_at else None,
        }

    def _dict_to_pet(self, pet_dict: dict) -> Pet:
        tasks = [self._dict_to_task(t) for t in pet_dict.get("tasks", [])]
        return Pet(
            id=pet_dict.get("id", ""),
            name=pet_dict.get("name", ""),
            animal=pet_dict.get("animal", ""),
            breed=pet_dict.get("breed", ""),
            age=pet_dict.get("age", 0),
            weight=pet_dict.get("weight", 0.0),
            tasks=tasks,
            health_info=pet_dict.get("health_info", {}),
            owner_id=pet_dict.get("owner_id", ""),
            created_at=self._parse_datetime(pet_dict.get("created_at"))
            or datetime.now(),
        )

    def _pet_to_dict(self, pet: Pet) -> dict:
        return {
            "id": pet.id,
            "name": pet.name,
            "animal": pet.animal,
            "breed": pet.breed,
            "age": pet.age,
            "weight": pet.weight,
            "tasks": [self._task_to_dict(t) for t in pet.tasks],
            "health_info": pet.health_info,
            "owner_id": pet.owner_id,
            "created_at": pet.created_at.isoformat() if pet.created_at else None,
        }

    def _dict_to_owner(self, owner_dict: dict) -> Owner:
        pets = [self._dict_to_pet(p) for p in owner_dict.get("pets", [])]
        return Owner(
            id=owner_dict.get("id", ""),
            name=owner_dict.get("name", ""),
            email=owner_dict.get("email", ""),
            pets=pets,
            preferences=owner_dict.get("preferences", {}),
            created_at=self._parse_datetime(owner_dict.get("created_at"))
            or datetime.now(),
        )

    def _owner_to_dict(self, owner: Owner) -> dict:
        return {
            "id": owner.id,
            "name": owner.name,
            "email": owner.email,
            "pets": [self._pet_to_dict(p) for p in owner.pets],
            "preferences": owner.preferences,
            "created_at": owner.created_at.isoformat() if owner.created_at else None,
        }

    def load_all(self) -> list[Owner]:
        data = self._load_data()
        owners = []
        for owner_dict in data.get("owners", []):
            owners.append(self._dict_to_owner(owner_dict))
        return owners

    def load_scheduler(self) -> Scheduler:
        scheduler = Scheduler()
        owners = self.load_all()
        for owner in owners:
            scheduler.register_owner(owner)
        return scheduler

    def save_all(self, owners: list[Owner]) -> None:
        data = {
            "owners": [self._owner_to_dict(o) for o in owners],
            "scheduler": {},
        }
        self._save_data(data)

    def save_scheduler(self, scheduler: Scheduler) -> None:
        owners = list(scheduler.owners.values())
        self.save_all(owners)


class CRUDExtensions:
    @staticmethod
    def create_owner(owners: list[Owner], owner: Owner, storage: DataStorage) -> Owner:
        owners.append(owner)
        storage.save_all(owners)
        return owner

    @staticmethod
    def read_owner(owners: list[Owner], owner_id: str) -> Optional[Owner]:
        for owner in owners:
            if owner.id == owner_id:
                return owner
        return None

    @staticmethod
    def update_owner(
        owners: list[Owner], owner_id: str, updates: dict, storage: DataStorage
    ) -> Optional[Owner]:
        for i, owner in enumerate(owners):
            if owner.id == owner_id:
                if "name" in updates:
                    owners[i].name = updates["name"]
                if "email" in updates:
                    owners[i].email = updates["email"]
                if "preferences" in updates:
                    owners[i].update_preferences(updates["preferences"])
                storage.save_all(owners)
                return owners[i]
        return None

    @staticmethod
    def delete_owner(owners: list[Owner], owner_id: str, storage: DataStorage) -> bool:
        for i, owner in enumerate(owners):
            if owner.id == owner_id:
                owners.pop(i)
                storage.save_all(owners)
                return True
        return False

    @staticmethod
    def create_pet(
        owners: list[Owner], owner_id: str, pet: Pet, storage: DataStorage
    ) -> Optional[Pet]:
        for owner in owners:
            if owner.id == owner_id:
                owner.add_pet(pet)
                storage.save_all(owners)
                return pet
        return None

    @staticmethod
    def read_pet(owners: list[Owner], pet_id: str) -> Optional[Pet]:
        for owner in owners:
            pet = owner.get_pet_by_id(pet_id)
            if pet:
                return pet
        return None

    @staticmethod
    def update_pet(
        owners: list[Owner], pet_id: str, updates: dict, storage: DataStorage
    ) -> Optional[Pet]:
        for owner in owners:
            for i, pet in enumerate(owner.pets):
                if pet.id == pet_id:
                    if "name" in updates:
                        owner.pets[i].name = updates["name"]
                    if "animal" in updates:
                        owner.pets[i].animal = updates["animal"]
                    if "breed" in updates:
                        owner.pets[i].breed = updates["breed"]
                    if "age" in updates:
                        owner.pets[i].age = updates["age"]
                    if "weight" in updates:
                        owner.pets[i].weight = updates["weight"]
                    storage.save_all(owners)
                    return owner.pets[i]
        return None

    @staticmethod
    def delete_pet(
        owners: list[Owner], owner_id: str, pet_id: str, storage: DataStorage
    ) -> bool:
        for owner in owners:
            if owner.id == owner_id:
                removed = owner.remove_pet(pet_id)
                if removed:
                    storage.save_all(owners)
                return removed
        return False

    @staticmethod
    def create_task(
        owners: list[Owner], pet_id: str, task: Task, storage: DataStorage
    ) -> Optional[Task]:
        for owner in owners:
            for pet in owner.pets:
                if pet.id == pet_id:
                    pet.add_task(task)
                    storage.save_all(owners)
                    return task
        return None

    @staticmethod
    def read_task(owners: list[Owner], task_id: str) -> Optional[Task]:
        for owner in owners:
            for pet in owner.pets:
                task = pet.get_task_by_id(task_id)
                if task:
                    return task
        return None

    @staticmethod
    def update_task(
        owners: list[Owner], task_id: str, updates: dict, storage: DataStorage
    ) -> Optional[Task]:
        for owner in owners:
            for pet in owner.pets:
                for i, task in enumerate(pet.tasks):
                    if task.id == task_id:
                        if "title" in updates:
                            pet.tasks[i].title = updates["title"]
                        if "description" in updates:
                            pet.tasks[i].description = updates["description"]
                        if "priority" in updates:
                            pet.tasks[i].priority = updates["priority"]
                        if "frequency" in updates:
                            pet.tasks[i].frequency = updates["frequency"]
                        if "assigned_date" in updates:
                            pet.tasks[i].assigned_date = updates["assigned_date"]
                        if "status" in updates:
                            pet.tasks[i].status = updates["status"]
                        storage.save_all(owners)
                        return pet.tasks[i]
        return None

    @staticmethod
    def delete_task(
        owners: list[Owner],
        owner_id: str,
        pet_id: str,
        task_id: str,
        storage: DataStorage,
    ) -> bool:
        for owner in owners:
            if owner.id == owner_id:
                removed = owner.get_pet_by_id(pet_id).remove_task(task_id)
                if removed:
                    storage.save_all(owners)
                return removed
        return False
