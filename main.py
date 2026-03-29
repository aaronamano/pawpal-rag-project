from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, TaskFrequency, TaskStatus, Scheduler


def main():
    owner = Owner(id="owner_1", name="Alex Johnson", email="alex@example.com")

    pet1 = Pet(id="pet_1", name="Buddy", animal="Dog", breed="Golden Retriever", age=3)
    pet2 = Pet(id="pet_2", name="Whiskers", animal="Cat", breed="Siamese", age=2)

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    scheduler = Scheduler()
    scheduler.register_owner(owner)

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
    scheduler.register_task(task1)

    task2 = Task(
        id="task_2",
        title="Feed Breakfast",
        description="1 cup of dry food",
        frequency=TaskFrequency.DAILY,
        priority=3,
        assigned_date=today.replace(hour=7, minute=30),
    )
    pet1.add_task(task2)
    scheduler.register_task(task2)

    task3 = Task(
        id="task_3",
        title="Grooming Session",
        description="Brush fur and clean ears",
        frequency=TaskFrequency.WEEKLY,
        priority=1,
        assigned_date=today.replace(hour=14),
    )
    pet2.add_task(task3)
    scheduler.register_task(task3)

    task4 = Task(
        id="task_4",
        title="Evening Playtime",
        description="Interactive toy session",
        frequency=TaskFrequency.DAILY,
        priority=2,
        assigned_date=today.replace(hour=18),
    )
    pet2.add_task(task4)
    scheduler.register_task(task4)

    print("=" * 60)
    print("          TODAY'S SCHEDULE")
    print(f"         {datetime.now().strftime('%B %d, %Y')}")
    print("=" * 60)
    print(f"\nOwner: {owner.name}")
    print(f"Pets: {', '.join(str(pet) for pet in owner.pets)}")
    print("\n" + "-" * 60)

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

    print("-" * 60)
    print(f"Total tasks: {len(all_tasks)}")

    print("\n" + "=" * 60)
    print("          CONFLICT DETECTION TEST")
    print("=" * 60)
    task5 = Task(
        id="task_5",
        title="Vet Checkup",
        description="Annual vaccination",
        frequency=TaskFrequency.ONE_TIME,
        priority=5,
        assigned_date=today.replace(hour=10),
    )
    pet1.add_task(task5)
    scheduler.register_task(task5)

    task6 = Task(
        id="task_6",
        title="Nail Trimming",
        description="Trim Buddy's nails",
        frequency=TaskFrequency.ONE_TIME,
        priority=4,
        assigned_date=today.replace(hour=10),
    )
    pet1.add_task(task6)
    scheduler.register_task(task6)

    print("\n[Added two tasks at same time: Vet Checkup & Nail Trimming at 10:00 AM]")
    print(scheduler.check_conflicts_warning())

    print("\n" + "=" * 60)
    print("          SORT BY OPTIONS TEST")
    print("=" * 60)
    schedule = scheduler.generate_schedule(owner.id, today)
    print("\nSorted by 'priority':")
    for t in schedule.generate_schedule(sort_by="priority"):
        print(
            f"  Priority {t.priority}: {t.title} at {t.assigned_date.strftime('%H:%M')}"
        )

    print("\nSorted by 'date':")
    for t in schedule.generate_schedule(sort_by="date"):
        print(f"  {t.assigned_date.strftime('%H:%M')}: {t.title}")

    print("\nSorted by 'pet_name':")
    for t in schedule.generate_schedule(sort_by="pet_name"):
        pet_name = next((p.name for p in owner.pets if p.id == t.pet_id), "Unknown")
        print(f"  {pet_name}: {t.title}")

    print("\nFiltered by status 'PENDING':")
    for t in schedule.generate_schedule(filter_status=TaskStatus.PENDING):
        print(f"  {t.title} - {t.status.value}")

    print("\n" + "=" * 60)
    print("          RECURRING TASK AUTO-RESCHEDULE TEST")
    print("=" * 60)
    print(f"\nCurrent task: {task2.title}")
    print(f"  Due: {task2.assigned_date}")
    print(f"  Frequency: {task2.frequency.value}")
    print(f"  Status: {task2.status.value}")

    new_task = scheduler.complete_task(task2.id)
    if new_task:
        print(f"\n[Task completed! Auto-rescheduled:]")
        print(f"  New task: {new_task.title}")
        print(f"  New due: {new_task.assigned_date}")
        print(f"  Status: {new_task.status.value}")

    print("\n" + "=" * 60)
    print("          SYSTEM STATS")
    print("=" * 60)
    stats = scheduler.get_system_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("          TASKS BY PRIORITY")
    print("=" * 60)
    high_priority = scheduler.get_tasks_by_priority(min_priority=3)
    for t in high_priority:
        print(f"  Priority {t.priority}: {t.title}")

    print("\n" + "=" * 60)
    print("          PET-SPECIFIC CONFLICTS")
    print("=" * 60)
    pet1_conflicts = scheduler.detect_conflicts(pet_id="pet_1")
    print(f"\nConflicts for pet_1 (Buddy): {len(pet1_conflicts)} found")
    for t1, t2 in pet1_conflicts:
        print(f"  - {t1.title} conflicts with {t2.title}")


if __name__ == "__main__":
    main()
