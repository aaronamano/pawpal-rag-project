from pawpal_system import Pet, Task, TaskStatus


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
