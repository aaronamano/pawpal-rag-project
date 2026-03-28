import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler, TaskStatus, TaskFrequency
from datetime import datetime
import uuid

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()
    st.session_state.owner = None

scheduler: Scheduler = st.session_state.scheduler

with st.expander("Owner Setup", expanded=True):
    owner_name = st.text_input("Owner Name", value="Jordan", key="owner_name")
    owner_email = st.text_input("Owner Email (optional)", value="", key="owner_email")

    if st.button("Create/Load Owner"):
        existing_owner = scheduler.get_owner_by_id("owner_1")
        if existing_owner:
            st.session_state.owner = existing_owner
            st.success(f"Loaded existing owner: {existing_owner.name}")
        else:
            new_owner = Owner(id="owner_1", name=owner_name, email=owner_email)
            scheduler.register_owner(new_owner)
            st.session_state.owner = new_owner
            st.success(f"Created new owner: {new_owner.name}")

    if st.session_state.owner:
        st.info(
            f"Current owner: {st.session_state.owner.name} ({len(st.session_state.owner.pets)} pets)"
        )

st.divider()

owner = st.session_state.owner

if owner:
    with st.expander("Add Pet", expanded=True):
        pet_name = st.text_input("Pet Name", key="pet_name_input")
        pet_species = st.selectbox(
            "Species",
            ["dog", "cat", "bird", "rabbit", "other"],
            key="pet_species_input",
        )
        pet_breed = st.text_input("Breed (optional)", key="pet_breed_input")
        pet_age = st.number_input(
            "Age (years)", min_value=0, max_value=50, value=1, key="pet_age_input"
        )
        pet_weight = st.number_input(
            "Weight (lbs)",
            min_value=0.0,
            max_value=500.0,
            value=10.0,
            key="pet_weight_input",
        )

        if st.button("Add Pet"):
            pet_id = f"pet_{uuid.uuid4().hex[:8]}"
            new_pet = Pet(
                id=pet_id,
                name=pet_name,
                animal=pet_species,
                breed=pet_breed,
                age=int(pet_age),
                weight=float(pet_weight),
            )
            owner.add_pet(new_pet)
            scheduler.register_pet(new_pet)
            st.success(f"Added pet: {new_pet.name}")
            st.rerun()

    st.divider()

    with st.expander("Add Task", expanded=True):
        if not owner.pets:
            st.warning("Add a pet first before creating tasks.")
        else:
            pet_options = {pet.name: pet for pet in owner.pets}
            selected_pet_name = st.selectbox(
                "Select Pet", list(pet_options.keys()), key="task_pet_select"
            )
            selected_pet = pet_options[selected_pet_name]

            task_title = st.text_input("Task Title", key="task_title_input")
            task_desc = st.text_area("Description", key="task_desc_input")
            task_priority = st.selectbox(
                "Priority",
                [1, 2, 3],
                index=2,
                format_func=lambda x: {1: "Low", 2: "Medium", 3: "High"}[x],
                key="task_priority_input",
            )
            task_frequency = st.selectbox(
                "Frequency", list(TaskFrequency), index=3, key="task_frequency_input"
            )

            if st.button("Add Task"):
                task_id = f"task_{uuid.uuid4().hex[:8]}"
                new_task = Task(
                    id=task_id,
                    title=task_title,
                    description=task_desc,
                    priority=task_priority,
                    frequency=task_frequency,
                    assigned_date=datetime.now(),
                )
                selected_pet.add_task(new_task)
                scheduler.register_task(new_task)
                st.success(f"Added task: {new_task.title} for {selected_pet.name}")
                st.rerun()

    st.divider()

    with st.expander("My Pets & Tasks", expanded=True):
        for pet in owner.pets:
            with st.container():
                st.subheader(f"🐾 {pet.name} ({pet.animal})")
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(
                        f"Breed: {pet.breed or 'N/A'} | Age: {pet.age} | Weight: {pet.weight} lbs"
                    )
                with col2:
                    counts = pet.get_task_count()
                    st.caption(
                        f"Tasks: {counts['pending']} pending, {counts['completed']} completed"
                    )

                tasks = pet.tasks
                if tasks:
                    task_data = []
                    for t in tasks:
                        status_str = t.status.value.capitalize()
                        if t.is_overdue():
                            status_str = "⚠️ Overdue"
                        elif t.status == TaskStatus.COMPLETED:
                            status_str = "✅ Completed"
                        elif t.status == TaskStatus.PENDING:
                            status_str = "⏳ Pending"
                        task_data.append(
                            {
                                "Title": t.title,
                                "Priority": {1: "Low", 2: "Medium", 3: "High"}[
                                    t.priority
                                ],
                                "Status": status_str,
                                "Action": t.id,
                            }
                        )
                    st.table(task_data)
                else:
                    st.info(f"No tasks for {pet.name} yet.")
                st.divider()

    st.divider()

    with st.expander("Generate Schedule", expanded=True):
        if st.button("Generate Schedule"):
            schedule = scheduler.generate_schedule(owner_id="owner_1")
            scheduled_tasks = schedule.generate_schedule()

            if scheduled_tasks:
                st.success(f"Generated schedule with {len(scheduled_tasks)} tasks:")
                for i, task in enumerate(scheduled_tasks, 1):
                    pet = scheduler.get_pet_by_id(task.pet_id)
                    pet_name = pet.name if pet else "Unknown"
                    st.markdown(
                        f"**{i}. {task.title}** ({pet_name}) - Priority: {task.priority}"
                    )
                    if task.description:
                        st.caption(f"   {task.description}")
            else:
                st.info("No tasks to schedule. Add some tasks first!")

            owner.add_schedule(schedule)

        if owner.schedules:
            st.subheader("Schedule History")
            for sched in owner.schedules:
                st.text(
                    f"Schedule {sched.id}: {sched.date.strftime('%Y-%m-%d %H:%M')} - {len(sched.scheduled_tasks)} tasks"
                )

else:
    st.info("👆 Create an owner first to get started!")

st.divider()

st.subheader("System Statistics")
stats = scheduler.get_system_stats()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Owners", stats["total_owners"])
col2.metric("Pets", stats["total_pets"])
col3.metric("Total Tasks", stats["total_tasks"])
col4.metric("Pending Tasks", stats["pending_tasks"])
