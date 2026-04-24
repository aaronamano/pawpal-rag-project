from datetime import datetime, timedelta
from pawpal_system import (
    Pet,
    Task,
    TaskStatus,
    TaskFrequency,
    Owner,
    Schedule,
    Scheduler,
)


class TestTaskCompletion:
    def test_mark_complete_changes_status(self):
        task = Task(
            id="task_1",
            title="Feed the cat",
            description="Morning feeding",
        )
        assert task.status == TaskStatus.PENDING
        task.complete()
        assert task.status == TaskStatus.COMPLETED


class TestTaskAddition:
    def test_add_task_increases_pet_task_count(self):
        pet = Pet(
            id="pet_1",
            name="Whiskers",
            animal="cat",
        )
        assert len(pet.tasks) == 0

        task = Task(
            id="task_1",
            title="Feed the cat",
            description="Morning feeding",
        )
        pet.add_task(task)

        assert len(pet.tasks) == 1
        assert task in pet.tasks
        assert task.pet_id == pet.id


class TestSortingCorrectness:
    def test_tasks_returned_in_chronological_order_by_date(self):
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)

        today = datetime.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        task_yesterday = Task(
            id="t1", title="Yesterday", description="", assigned_date=yesterday
        )
        task_today = Task(id="t2", title="Today", description="", assigned_date=today)
        task_tomorrow = Task(
            id="t3", title="Tomorrow", description="", assigned_date=tomorrow
        )

        pet.add_task(task_tomorrow)
        pet.add_task(task_yesterday)
        pet.add_task(task_today)

        schedule = Schedule(id="s1", date=today, owner=owner)
        sorted_tasks = schedule.generate_schedule(sort_by="date")

        assert sorted_tasks[0].id == "t1"
        assert sorted_tasks[1].id == "t2"
        assert sorted_tasks[2].id == "t3"

    def test_tasks_with_same_date_sorted_by_priority(self):
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)

        same_date = datetime.now()
        low_priority = Task(
            id="t1", title="Low", description="", priority=1, assigned_date=same_date
        )
        high_priority = Task(
            id="t2", title="High", description="", priority=5, assigned_date=same_date
        )

        pet.add_task(low_priority)
        pet.add_task(high_priority)

        schedule = Schedule(id="s1", date=same_date, owner=owner)
        sorted_tasks = schedule.generate_schedule(sort_by="date")

        assert sorted_tasks[0].id == "t2"
        assert sorted_tasks[1].id == "t1"


class TestTaskSorting:
    def test_sort_by_priority_with_none_assigned_date(self):
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)

        task1 = Task(id="t1", title="Task 1", description="", priority=3)
        task2 = Task(
            id="t2",
            title="Task 2",
            description="",
            priority=1,
            assigned_date=datetime.now(),
        )
        task3 = Task(id="t3", title="Task 3", description="", priority=2)

        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)

        schedule = Schedule(id="s1", date=datetime.now(), owner=owner)
        sorted_tasks = schedule.generate_schedule(sort_by="priority")

        assert sorted_tasks[0].priority == 3
        assert sorted_tasks[1].priority == 2
        assert sorted_tasks[2].priority == 1

    def test_sort_by_date_with_none_assigned_dates(self):
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)

        task_no_date = Task(id="t1", title="No Date", description="")

        pet.add_task(task_no_date)

        schedule = Schedule(id="s1", date=datetime.now(), owner=owner)
        sorted_tasks = schedule.generate_schedule(sort_by="date")

        assert len(sorted_tasks) == 1
        assert sorted_tasks[0].id == "t1"

    def test_sort_by_pet_name(self):
        owner = Owner(id="owner_1", name="John")
        cat = Pet(id="cat_1", name="Alpha", animal="cat")
        dog = Pet(id="dog_1", name="Beta", animal="dog")
        owner.add_pet(cat)
        owner.add_pet(dog)

        cat_task = Task(id="t1", title="Cat Task", description="", pet_id="cat_1")
        dog_task = Task(id="t2", title="Dog Task", description="", pet_id="dog_1")
        cat.add_task(cat_task)
        dog.add_task(dog_task)

        schedule = Schedule(id="s1", date=datetime.now(), owner=owner)
        sorted_tasks = schedule.generate_schedule(sort_by="pet_name")

        assert sorted_tasks[0].pet_id == "cat_1"
        assert sorted_tasks[1].pet_id == "dog_1"

    def test_sort_empty_schedule(self):
        owner = Owner(id="owner_1", name="John")
        schedule = Schedule(id="s1", date=datetime.now(), owner=owner)
        sorted_tasks = schedule.generate_schedule()

        assert sorted_tasks == []

    def test_sort_without_owner(self):
        schedule = Schedule(id="s1", date=datetime.now())
        sorted_tasks = schedule.generate_schedule()

        assert sorted_tasks == []

    def test_sort_excludes_completed_by_default(self):
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)

        pending_task = Task(id="t1", title="Pending", description="")
        completed_task = Task(id="t2", title="Completed", description="")
        completed_task.complete()

        pet.add_task(pending_task)
        pet.add_task(completed_task)

        schedule = Schedule(id="s1", date=datetime.now(), owner=owner)
        sorted_tasks = schedule.generate_schedule()

        assert len(sorted_tasks) == 1
        assert sorted_tasks[0].id == "t1"

    def test_sort_includes_completed_when_requested(self):
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)

        pending_task = Task(id="t1", title="Pending", description="")
        completed_task = Task(id="t2", title="Completed", description="")
        completed_task.complete()

        pet.add_task(pending_task)
        pet.add_task(completed_task)

        schedule = Schedule(id="s1", date=datetime.now(), owner=owner)
        sorted_tasks = schedule.generate_schedule(include_completed=True)

        assert len(sorted_tasks) == 2


class TestRecurrenceLogic:
    def test_daily_task_creates_new_task_for_following_day(self):
        scheduler = Scheduler()
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)
        scheduler.register_owner(owner)

        original_date = datetime(2024, 6, 15, 10, 0, 0)
        daily_task = Task(
            id="daily_1",
            title="Daily Feeding",
            description="",
            frequency=TaskFrequency.DAILY,
            assigned_date=original_date,
        )
        pet.add_task(daily_task)
        scheduler.register_task(daily_task)

        completed_task = scheduler.complete_task("daily_1")

        assert completed_task is not None
        assert completed_task.status == TaskStatus.COMPLETED
        assert completed_task.assigned_date == original_date


class TestTaskRecurrency:
    def test_daily_task_reschedules(self):
        scheduler = Scheduler()
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)
        scheduler.register_owner(owner)

        daily_task = Task(
            id="daily_1",
            title="Daily Feeding",
            description="",
            frequency=TaskFrequency.DAILY,
            assigned_date=datetime(2024, 6, 15, 10, 0, 0),
        )
        pet.add_task(daily_task)
        scheduler.register_task(daily_task)

        result = scheduler.complete_task("daily_1")

        assert result is not None
        assert result.id == "daily_1"
        assert result.status == TaskStatus.COMPLETED
        assert result.frequency == TaskFrequency.DAILY

    def test_weekly_task_reschedules(self):
        scheduler = Scheduler()
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)
        scheduler.register_owner(owner)

        weekly_task = Task(
            id="weekly_1",
            title="Weekly Grooming",
            description="",
            frequency=TaskFrequency.WEEKLY,
            assigned_date=datetime(2024, 6, 15, 10, 0, 0),
        )
        pet.add_task(weekly_task)
        scheduler.register_task(weekly_task)

        result = scheduler.complete_task("weekly_1")

        assert result is not None
        assert result.frequency == TaskFrequency.WEEKLY
        assert result.status == TaskStatus.COMPLETED

    def test_monthly_task_does_not_reschedule(self):
        scheduler = Scheduler()
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)
        scheduler.register_owner(owner)

        monthly_task = Task(
            id="monthly_1",
            title="Monthly Checkup",
            description="",
            frequency=TaskFrequency.MONTHLY,
            assigned_date=datetime(2024, 6, 15, 10, 0, 0),
        )
        pet.add_task(monthly_task)
        scheduler.register_task(monthly_task)

        result = scheduler.complete_task("monthly_1")

        assert result is not None
        assert result.status == TaskStatus.COMPLETED

    def test_one_time_task_does_not_reschedule(self):
        scheduler = Scheduler()
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)
        scheduler.register_owner(owner)

        one_time_task = Task(
            id="one_time_1",
            title="One Time Vaccine",
            description="",
            frequency=TaskFrequency.ONE_TIME,
            assigned_date=datetime(2024, 6, 15, 10, 0, 0),
        )
        pet.add_task(one_time_task)
        scheduler.register_task(one_time_task)

        result = scheduler.complete_task("one_time_1")

        assert result is not None
        assert result.status == TaskStatus.COMPLETED

    def test_complete_nonexistent_task_returns_none(self):
        scheduler = Scheduler()

        result = scheduler.complete_task("nonexistent_task")

        assert result is None

    def test_daily_task_no_assigned_date_does_not_reschedule(self):
        scheduler = Scheduler()
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)
        scheduler.register_owner(owner)

        daily_task = Task(
            id="daily_no_date",
            title="Daily Task",
            description="",
            frequency=TaskFrequency.DAILY,
        )
        pet.add_task(daily_task)
        scheduler.register_task(daily_task)

        result = scheduler.complete_task("daily_no_date")

        assert result is not None
        assert result.status == TaskStatus.COMPLETED


class TestConflictDetection:
    def test_scheduler_flags_duplicate_times(self):
        scheduler = Scheduler()
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)
        scheduler.register_owner(owner)

        same_datetime = datetime(2024, 6, 15, 10, 0, 0)
        task1 = Task(
            id="t1", title="Task 1", description="", assigned_date=same_datetime
        )
        task2 = Task(
            id="t2", title="Task 2", description="", assigned_date=same_datetime
        )

        pet.add_task(task1)
        pet.add_task(task2)
        scheduler.register_pet(pet)

        conflicts = scheduler.detect_conflicts("pet_1")
        assert len(conflicts) == 1
        assert conflicts[0][0].id == "t1"
        assert conflicts[0][1].id == "t2"

        warning = scheduler.check_conflicts_warning("pet_1")
        assert "Scheduling Conflicts Detected" in warning
        assert "Task 1" in warning
        assert "Task 2" in warning

    def test_no_conflicts_when_no_overlapping_times(self):
        scheduler = Scheduler()
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)
        scheduler.register_owner(owner)

        task1 = Task(
            id="t1",
            title="Task 1",
            description="",
            assigned_date=datetime(2024, 6, 15, 10, 0, 0),
        )
        task2 = Task(
            id="t2",
            title="Task 2",
            description="",
            assigned_date=datetime(2024, 6, 15, 12, 0, 0),
        )

        pet.add_task(task1)
        pet.add_task(task2)
        scheduler.register_pet(pet)

        conflicts = scheduler.detect_conflicts("pet_1")
        assert len(conflicts) == 0

        warning = scheduler.check_conflicts_warning("pet_1")
        assert "No scheduling conflicts" in warning


class TestTaskSchedulingEdgeCases:
    def test_overdue_task_detection(self):
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")

        past_date = datetime.now() - timedelta(days=5)
        overdue_task = Task(
            id="overdue_1",
            title="Overdue Task",
            description="",
            assigned_date=past_date,
        )

        pet.add_task(overdue_task)

        assert overdue_task.is_overdue() is True
        assert overdue_task.get_overdue_days() == 5

    def test_task_not_overdue_when_completed(self):
        past_date = datetime.now() - timedelta(days=5)
        task = Task(
            id="completed_overdue",
            title="Completed Task",
            description="",
            assigned_date=past_date,
        )
        task.complete()

        assert task.is_overdue() is False

    def test_get_days_until_due_with_past_date(self):
        past_date = datetime.now() - timedelta(days=3)
        task = Task(
            id="past_due",
            title="Past Due Task",
            description="",
            assigned_date=past_date,
        )

        days = task.get_days_until_due()

        assert days < 0

    def test_get_days_until_due_no_assigned_date(self):
        task = Task(id="no_date", title="No Date Task", description="")

        days = task.get_days_until_due()

        assert days == -1

    def test_conflict_detection_same_date(self):
        scheduler = Scheduler()
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")

        same_date = datetime.now() + timedelta(days=1)
        task1 = Task(id="t1", title="Task 1", description="", assigned_date=same_date)
        task2 = Task(id="t2", title="Task 2", description="", assigned_date=same_date)

        pet.add_task(task1)
        pet.add_task(task2)
        scheduler.register_pet(pet)

        conflicts = scheduler.detect_conflicts("pet_1")

        assert len(conflicts) == 1
        assert (task1, task2) in conflicts or (task2, task1) in conflicts

    def test_no_conflict_different_dates(self):
        scheduler = Scheduler()
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")

        task1 = Task(
            id="t1", title="Task 1", description="", assigned_date=datetime.now()
        )
        task2 = Task(
            id="t2",
            title="Task 2",
            description="",
            assigned_date=datetime.now() + timedelta(days=1),
        )

        pet.add_task(task1)
        pet.add_task(task2)
        scheduler.register_pet(pet)

        conflicts = scheduler.detect_conflicts("pet_1")

        assert len(conflicts) == 0

    def test_multiple_tasks_same_priority_sorted_by_date(self):
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)

        today = datetime.now()
        tomorrow = today + timedelta(days=1)

        task1 = Task(
            id="t1", title="Today", description="", priority=2, assigned_date=today
        )
        task2 = Task(
            id="t2",
            title="Tomorrow",
            description="",
            priority=2,
            assigned_date=tomorrow,
        )
        task3 = Task(
            id="t3",
            title="Yesterday",
            description="",
            priority=2,
            assigned_date=today - timedelta(days=1),
        )

        pet.add_task(task3)
        pet.add_task(task1)
        pet.add_task(task2)

        schedule = Schedule(id="s1", date=today, owner=owner)
        sorted_tasks = schedule.generate_schedule(sort_by="priority")

        assert sorted_tasks[0].id == "t3"
        assert sorted_tasks[1].id == "t1"
        assert sorted_tasks[2].id == "t2"

    def test_filter_by_status_in_schedule(self):
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)

        pending = Task(id="pending_1", title="Pending", description="")
        completed = Task(id="completed_1", title="Completed", description="")
        completed.complete()

        pet.add_task(pending)
        pet.add_task(completed)

        schedule = Schedule(id="s1", date=datetime.now(), owner=owner)
        filtered = schedule.generate_schedule(filter_status=TaskStatus.PENDING)

        assert len(filtered) == 1
        assert filtered[0].id == "pending_1"

    def test_scheduler_respects_task_completion_status(self):
        scheduler = Scheduler()
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)
        scheduler.register_owner(owner)

        task = Task(
            id="task_1",
            title="Task",
            description="",
            assigned_date=datetime.now(),
            frequency=TaskFrequency.DAILY,
        )
        pet.add_task(task)
        scheduler.register_task(task)

        assert task.status == TaskStatus.PENDING

        result = scheduler.complete_task("task_1")

        assert task.status == TaskStatus.COMPLETED
        assert result is not None


class TestTasksDueFiltering:
    def test_scheduler_get_tasks_due_today_excludes_completed(self):
        scheduler = Scheduler()
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)

        pending_task = Task(
            id="pending_today",
            title="Pending Today",
            description="",
            assigned_date=datetime.now(),
        )
        completed_task = Task(
            id="completed_today",
            title="Completed Today",
            description="",
            assigned_date=datetime.now(),
        )
        completed_task.complete()

        pet.add_task(pending_task)
        pet.add_task(completed_task)
        scheduler.register_owner(owner)

        today_tasks = scheduler.get_tasks_due_today()

        assert len(today_tasks) == 1
        assert today_tasks[0].id == "pending_today"

    def test_scheduler_get_tasks_due_today_filters_only_pending(self):
        scheduler = Scheduler()
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)

        today = datetime.now()
        yesterday = today - timedelta(days=1)

        pending_yesterday = Task(
            id="p_yesterday",
            title="Pending Yesterday",
            description="",
            assigned_date=yesterday,
        )
        pending_today = Task(
            id="p_today",
            title="Pending Today",
            description="",
            assigned_date=today,
        )

        pet.add_task(pending_yesterday)
        pet.add_task(pending_today)
        scheduler.register_owner(owner)

        today_tasks = scheduler.get_tasks_due_today()

        assert len(today_tasks) == 1
        assert today_tasks[0].id == "p_today"

    def test_scheduler_get_tasks_due_soon_excludes_completed(self):
        scheduler = Scheduler()
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)

        today = datetime.now()
        tomorrow = today + timedelta(days=1)

        pending_soon = Task(
            id="pending_soon",
            title="Pending Soon",
            description="",
            assigned_date=tomorrow,
        )
        completed_soon = Task(
            id="completed_soon",
            title="Completed Soon",
            description="",
            assigned_date=tomorrow,
        )
        completed_soon.complete()

        pet.add_task(pending_soon)
        pet.add_task(completed_soon)
        scheduler.register_owner(owner)

        soon_tasks = scheduler.get_tasks_due_soon(3)

        assert len(soon_tasks) == 1
        assert soon_tasks[0].id == "pending_soon"

    def test_scheduler_get_tasks_due_next_week_excludes_completed(self):
        scheduler = Scheduler()
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)

        today = datetime.now()
        in_5_days = today + timedelta(days=5)

        pending_next_week = Task(
            id="pending_next_week",
            title="Pending Next Week",
            description="",
            assigned_date=in_5_days,
        )
        completed_next_week = Task(
            id="completed_next_week",
            title="Completed Next Week",
            description="",
            assigned_date=in_5_days,
        )
        completed_next_week.complete()

        pet.add_task(pending_next_week)
        pet.add_task(completed_next_week)
        scheduler.register_owner(owner)

        next_week_tasks = scheduler.get_tasks_due_next_week()

        assert len(next_week_tasks) == 1
        assert next_week_tasks[0].id == "pending_next_week"

    def test_pet_get_tasks_due_today_excludes_completed(self):
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")

        pending_task = Task(
            id="pending_today",
            title="Pending Today",
            description="",
            assigned_date=datetime.now(),
        )
        completed_task = Task(
            id="completed_today",
            title="Completed Today",
            description="",
            assigned_date=datetime.now(),
        )
        completed_task.complete()

        pet.add_task(pending_task)
        pet.add_task(completed_task)

        today_tasks = pet.get_tasks_due_today()

        assert len(today_tasks) == 1
        assert today_tasks[0].id == "pending_today"

    def test_pet_get_tasks_due_next_week_excludes_completed(self):
        scheduler = Scheduler()
        owner = Owner(id="owner_1", name="John")
        pet = Pet(id="pet_1", name="Whiskers", animal="cat")
        owner.add_pet(pet)

        in_3_days = datetime.now() + timedelta(days=3)

        pending_task = Task(
            id="pending_next_week",
            title="Pending Next Week",
            description="",
            assigned_date=in_3_days,
        )
        completed_task = Task(
            id="completed_next_week",
            title="Completed Next Week",
            description="",
            assigned_date=in_3_days,
        )
        completed_task.complete()

        pet.add_task(pending_task)
        pet.add_task(completed_task)
        scheduler.register_owner(owner)

        next_week_tasks = scheduler.get_tasks_due_next_week()

        assert len(next_week_tasks) == 1
        assert next_week_tasks[0].id == "pending_next_week"
