import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import Optional
from data_storage import DataStorage, CRUDExtensions
from pawpal_system import (
    Task,
    Pet,
    Owner,
    Scheduler,
    TaskStatus,
    TaskFrequency,
    Schedule,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "pawpal_data.json"
storage = DataStorage(DATA_FILE)

scheduler: Scheduler = storage.load_scheduler()
owners: list[Owner] = storage.load_all()


def reload_data():
    global scheduler, owners
    scheduler = storage.load_scheduler()
    owners = storage.load_all()


class TaskCreate(BaseModel):
    title: str
    description: str = ""
    priority: int = 1
    frequency: str = "one_time"
    assigned_date: Optional[str] = None
    pet_id: str


class PetCreate(BaseModel):
    name: str
    animal: str
    breed: str = ""
    age: int = 0
    weight: float = 0.0
    owner_id: str


class OwnerCreate(BaseModel):
    name: str
    email: str = ""


@app.get("/api/stats")
def get_stats():
    reload_data()
    return scheduler.get_system_stats()


@app.get("/")
def root():
    return {"message": "PawPal+ API is running"}


@app.get("/docs", include_in_schema=False)
def docs():
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/docs")


@app.get("/api/owners")
def get_owners():
    reload_data()
    return [
        {
            "id": o.id,
            "name": o.name,
            "email": o.email,
            "pets": [
                {
                    "id": p.id,
                    "name": p.name,
                    "animal": p.animal,
                    "breed": p.breed,
                    "age": p.age,
                    "weight": p.weight,
                    "tasks": [
                        {
                            "id": t.id,
                            "title": t.title,
                            "description": t.description,
                            "priority": t.priority,
                            "frequency": t.frequency.value,
                            "assigned_date": t.assigned_date.isoformat()
                            if t.assigned_date
                            else None,
                            "status": t.status.value,
                            "pet_id": t.pet_id,
                        }
                        for t in p.tasks
                    ],
                }
                for p in o.pets
            ],
        }
        for o in owners
    ]


@app.post("/api/owners")
def create_owner(data: OwnerCreate):
    reload_data()
    new_owner = Owner(
        id=f"owner_{uuid.uuid4().hex[:8]}",
        name=data.name,
        email=data.email,
    )
    CRUDExtensions.create_owner(owners, new_owner, storage)
    reload_data()
    return {"id": new_owner.id, "name": new_owner.name}


@app.delete("/api/owners/{owner_id}")
def delete_owner(owner_id: str):
    reload_data()
    CRUDExtensions.delete_owner(owners, owner_id, storage)
    reload_data()
    return {"success": True}


@app.post("/api/pets")
def create_pet(data: PetCreate):
    reload_data()
    pet_id = f"pet_{uuid.uuid4().hex[:8]}"
    new_pet = Pet(
        id=pet_id,
        name=data.name,
        animal=data.animal,
        breed=data.breed,
        age=data.age,
        weight=data.weight,
    )
    CRUDExtensions.create_pet(owners, data.owner_id, new_pet, storage)
    reload_data()
    return {"id": new_pet.id, "name": new_pet.name}


@app.delete("/api/pets/{pet_id}")
def delete_pet(pet_id: str):
    reload_data()
    for owner in owners:
        removed = owner.remove_pet(pet_id)
        if removed:
            storage.save_all(owners)
            break
    reload_data()
    return {"success": True}


@app.post("/api/tasks")
def create_task(data: TaskCreate):
    reload_data()
    task_datetime = None
    if data.assigned_date:
        try:
            task_datetime = datetime.fromisoformat(data.assigned_date)
        except:
            pass

    task_id = f"task_{uuid.uuid4().hex[:8]}"
    new_task = Task(
        id=task_id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        frequency=TaskFrequency(data.frequency),
        assigned_date=task_datetime,
    )
    CRUDExtensions.create_task(owners, data.pet_id, new_task, storage)
    reload_data()
    return {"id": new_task.id, "title": new_task.title}


@app.post("/api/tasks/{task_id}/complete")
def complete_task(task_id: str):
    reload_data()
    scheduler.complete_task(task_id)
    storage.save_scheduler(scheduler)
    reload_data()
    return {"success": True}


@app.post("/api/tasks/{task_id}/pending")
def mark_task_pending(task_id: str):
    reload_data()
    task = scheduler.get_task_by_id(task_id)
    if task:
        task.mark_pending()
        storage.save_scheduler(scheduler)
        reload_data()
    return {"success": True}


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: str):
    reload_data()
    for owner in owners:
        for pet in owner.pets:
            removed = pet.remove_task(task_id)
            if removed:
                storage.save_all(owners)
                reload_data()
                return {"success": True}
    return {"success": False}


@app.get("/api/schedule/{owner_id}")
def get_schedule(owner_id: str):
    reload_data()
    schedule = scheduler.generate_schedule(owner_id)
    scheduled_tasks = schedule.generate_schedule(
        include_completed=False,
        sort_by="priority",
    )
    return [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "priority": t.priority,
            "frequency": t.frequency.value,
            "assigned_date": t.assigned_date.isoformat() if t.assigned_date else None,
            "status": t.status.value,
            "pet_id": t.pet_id,
            "pet_name": scheduler.get_pet_by_id(t.pet_id).name
            if scheduler.get_pet_by_id(t.pet_id)
            else "?",
        }
        for t in scheduled_tasks
    ]


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
