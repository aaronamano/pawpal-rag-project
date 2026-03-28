from datetime import datetime
from pawpal_system import Owner, Pet, Task, TaskFrequency, TaskStatus


def main():
    owner = Owner(id="owner_1", name="Alex Johnson", email="alex@example.com")

    pet1 = Pet(id="pet_1", name="Buddy", animal="Dog", breed="Golden Retriever", age=3)
    pet2 = Pet(id="pet_2", name="Whiskers", animal="Cat", breed="Siamese", age=2)

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    task1 = Task(
        id="task_1",
        title="Morning Walk",
        description="30-minute walk in the park",
        frequency=TaskFrequency.DAILY,
        priority=2,
        assigned_date=today.replace(hour=8),
    )
    pet1.add_task(task1)

    task2 = Task(
        id="task_2",
        title="Feed Breakfast",
        description="1 cup of dry food",
        frequency=TaskFrequency.DAILY,
        priority=3,
        assigned_date=today.replace(hour=7, minute=30),
    )
    pet1.add_task(task2)

    task3 = Task(
        id="task_3",
        title="Grooming Session",
        description="Brush fur and clean ears",
        frequency=TaskFrequency.WEEKLY,
        priority=1,
        assigned_date=today.replace(hour=14),
    )
    pet2.add_task(task3)

    task4 = Task(
        id="task_4",
        title="Evening Playtime",
        description="Interactive toy session",
        frequency=TaskFrequency.DAILY,
        priority=2,
        assigned_date=today.replace(hour=18),
    )
    pet2.add_task(task4)

    print("=" * 50)
    print("          TODAY'S SCHEDULE")
    print(f"         {datetime.now().strftime('%B %d, %Y')}")
    print("=" * 50)
    print(f"\nOwner: {owner.name}")
    print(f"Pets: {', '.join(str(pet) for pet in owner.pets)}")
    print("\n" + "-" * 50)

    all_tasks = owner.get_all_tasks()
    all_tasks.sort(key=lambda t: t.assigned_date or datetime.min)

    for task in all_tasks:
        time_str = (
            task.assigned_date.strftime("%I:%M %p") if task.assigned_date else "No time"
        )
        pet_name = next((p.name for p in owner.pets if p.id == task.pet_id), "Unknown")
        status_icon = (
            "✓"
            if task.status == TaskStatus.COMPLETED
            else ("!" if task.is_overdue() else "○")
        )
        print(f"  {time_str}  {status_icon} {task.title}")
        print(f"          Pet: {pet_name} | Priority: {task.priority}")
        print()

    print("-" * 50)
    print(f"Total tasks: {len(all_tasks)}")


if __name__ == "__main__":
    main()
