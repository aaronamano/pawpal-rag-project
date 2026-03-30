import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler, TaskStatus, TaskFrequency
from datetime import datetime
import uuid

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()
    st.session_state.owner = None

scheduler: Scheduler = st.session_state.scheduler

st.title("🐾 PawPal+ Dashboard")

col_stats1, col_stats2, col_stats3, col_stats4, col_stats5 = st.columns(5)
with col_stats1:
    st.markdown("### 👤 Owners")
    st.markdown(f"**{scheduler.get_system_stats()['total_owners']}**")
with col_stats2:
    st.markdown("### 🐾 Pets")
    st.markdown(f"**{scheduler.get_system_stats()['total_pets']}**")
with col_stats3:
    st.markdown("### 📋 Total Tasks")
    st.markdown(f"**{scheduler.get_system_stats()['total_tasks']}**")
with col_stats4:
    st.markdown("### ⏳ Pending")
    st.markdown(f"**{scheduler.get_system_stats()['pending_tasks']}**")
with col_stats5:
    overdue = scheduler.get_system_stats()["overdue_tasks"]
    st.markdown("### ⚠️ Overdue")
    st.markdown(f"**{overdue}**" if overdue > 0 else "**0**")

st.divider()

owner = st.session_state.owner

main_col1, main_col2, main_col3 = st.columns(3)

with main_col1:
    with st.container(border=True):
        st.markdown("#### 👤 Owner Setup")
        owner_name = st.text_input(
            "Name",
            value="Jordan",
            key="owner_name",
            label_visibility="collapsed",
            placeholder="Owner Name",
        )
        owner_email = st.text_input(
            "Email",
            value="",
            key="owner_email",
            label_visibility="collapsed",
            placeholder="Email (optional)",
        )

        if st.button("Create / Load Owner", use_container_width=True, type="primary"):
            existing_owner = scheduler.get_owner_by_id("owner_1")
            if existing_owner:
                st.session_state.owner = existing_owner
                st.success(f"✅ Loaded: {existing_owner.name}")
            else:
                new_owner = Owner(id="owner_1", name=owner_name, email=owner_email)
                scheduler.register_owner(new_owner)
                st.session_state.owner = new_owner
                st.success(f"✅ Created: {new_owner.name}")

        if st.session_state.owner:
            st.caption(
                f"**Current:** {st.session_state.owner.name} | 🐾 {len(st.session_state.owner.pets)} pets"
            )

with main_col2:
    with st.container(border=True):
        st.markdown("#### ➕ Add Pet")
        pet_name = st.text_input(
            "Pet Name",
            key="pet_name_input",
            label_visibility="collapsed",
            placeholder="Pet Name",
        )
        pet_species = st.selectbox(
            "Species",
            ["dog", "cat", "bird", "rabbit", "other"],
            key="pet_species_input",
        )

        c1, c2 = st.columns(2)
        with c1:
            pet_age = st.number_input(
                "Age (yrs)", min_value=0, max_value=50, value=1, key="pet_age_input"
            )
        with c2:
            pet_weight = st.number_input(
                "Weight (lbs)",
                min_value=0.0,
                max_value=500.0,
                value=10.0,
                key="pet_weight_input",
            )

        pet_breed = st.text_input(
            "Breed",
            key="pet_breed_input",
            label_visibility="collapsed",
            placeholder="Breed (optional)",
        )

        if st.button(
            "Add Pet", use_container_width=True, type="primary", disabled=not owner
        ):
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
            st.success(f"✅ Added: {new_pet.name}")
            st.rerun()

        if not owner:
            st.caption("⚠️ Create owner first")

with main_col3:
    with st.container(border=True):
        st.markdown("#### 📋 Add Task")

        if not owner or not owner.pets:
            st.warning("⚠️ Add a pet first")
        else:
            pet_options = {pet.name: pet for pet in owner.pets}
            selected_pet_name = st.selectbox(
                "Select Pet", list(pet_options.keys()), key="task_pet_select"
            )
            selected_pet = pet_options[selected_pet_name]

            task_title = st.text_input(
                "Task Title",
                key="task_title_input",
                label_visibility="collapsed",
                placeholder="Task Title",
            )
            task_priority = st.selectbox(
                "Priority",
                [1, 2, 3],
                index=2,
                format_func=lambda x: {1: "📘 Low", 2: "🟡 Medium", 3: "🔴 High"}[x],
                key="task_priority_input",
            )
            task_frequency = st.selectbox(
                "Frequency", list(TaskFrequency), index=3, key="task_frequency_input"
            )
            task_desc = st.text_area(
                "Description",
                key="task_desc_input",
                label_visibility="collapsed",
                placeholder="Description (optional)",
                max_chars=200,
            )

            if st.button("Add Task", use_container_width=True, type="primary"):
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
                st.success(f"✅ Task added for {selected_pet.name}")
                st.rerun()

st.divider()

if owner:
    tab1, tab2, tab3 = st.tabs(["🐾 Pets & Tasks", "📊 Dashboard", "📅 Schedule"])

    with tab1:
        if not owner.pets:
            st.info("No pets yet. Add a pet using the form above!")
        else:
            cols = (
                st.columns(len(owner.pets)) if len(owner.pets) <= 4 else st.columns(4)
            )

            for idx, pet in enumerate(owner.pets[:4]):
                with cols[idx]:
                    counts = pet.get_task_count()

                    with st.container(border=True):
                        emoji = {
                            "dog": "🐕",
                            "cat": "🐈",
                            "bird": "🐦",
                            "rabbit": "🐰",
                        }.get(pet.animal, "🐾")
                        st.markdown(f"### {emoji} {pet.name}")
                        st.caption(
                            f"**{pet.animal.title()}** | {pet.breed or 'N/A'} | {pet.age} yrs | {pet.weight} lbs"
                        )

                        mc1, mc2, mc3, mc4 = st.columns(4)
                        mc1.metric("Total", counts["total"])
                        mc2.metric("✅ Done", counts["completed"])
                        mc3.metric("⏳", counts["pending"])
                        mc4.metric("⚠️", counts["overdue"])

                        with st.expander(f"View Tasks ({len(pet.tasks)})"):
                            if pet.tasks:
                                header_cols = st.columns([3, 1, 1, 1, 1])
                                with header_cols[0]:
                                    st.markdown("**Task**")
                                with header_cols[1]:
                                    st.markdown("**Done**")
                                with header_cols[2]:
                                    st.markdown("**Priority**")
                                with header_cols[3]:
                                    st.markdown("**Status**")
                                with header_cols[4]:
                                    st.markdown("**Freq**")

                                for t in pet.tasks:
                                    status = t.status.value.capitalize()
                                    if t.is_overdue():
                                        status = "⚠️ Overdue"
                                    elif t.status == TaskStatus.COMPLETED:
                                        status = "✅ Done"
                                    else:
                                        status = "⏳ Pending"

                                    priority_map = {
                                        1: "📘 Low",
                                        2: "🟡 Med",
                                        3: "🔴 High",
                                    }
                                    is_completed = t.status == TaskStatus.COMPLETED

                                    task_cols = st.columns([3, 1, 1, 1, 1])
                                    with task_cols[0]:
                                        st.caption(
                                            f"{t.title[:30]}{'...' if len(t.title) > 30 else ''}"
                                        )
                                    with task_cols[1]:
                                        checked = st.checkbox(
                                            "",
                                            value=is_completed,
                                            key=f"pet_task_{t.id}",
                                            label_visibility="hidden",
                                        )
                                        if checked and t.status != TaskStatus.COMPLETED:
                                            scheduler.complete_task(t.id)
                                            st.rerun()
                                        elif (
                                            not checked
                                            and t.status == TaskStatus.COMPLETED
                                        ):
                                            t.mark_pending()
                                            st.rerun()
                                    with task_cols[2]:
                                        st.caption(priority_map.get(t.priority, ""))
                                    with task_cols[3]:
                                        st.caption(status)
                                    with task_cols[4]:
                                        st.caption(t.frequency.value[:3].title())
                            else:
                                st.caption("No tasks yet")

    with tab2:
        all_tasks = owner.get_all_tasks()

        if not all_tasks:
            st.info("No tasks yet. Create tasks to see the dashboard!")
        else:
            pending = owner.get_all_pending_tasks()
            overdue = owner.get_all_overdue_tasks()
            completed = [t for t in all_tasks if t.status == TaskStatus.COMPLETED]

            kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
            kpi1.metric("Total Tasks", len(all_tasks))
            kpi2.metric("Pending", len(pending))
            kpi3.metric("Completed", len(completed))
            kpi4.metric("Overdue", len(overdue))
            kpi5.metric("Pets", len(owner.pets))

            st.divider()

            col_filt, col_sort = st.columns([1, 1])
            with col_filt:
                dash_filter = st.selectbox(
                    "Filter",
                    ["All Tasks", "Pending", "Completed", "Overdue"],
                    key="dash_filter",
                )
            with col_sort:
                dash_sort = st.selectbox(
                    "Sort by", ["Priority", "Date", "Pet Name"], key="dash_sort"
                )

            display_tasks = all_tasks
            if dash_filter == "Pending":
                display_tasks = pending
            elif dash_filter == "Completed":
                display_tasks = completed
            elif dash_filter == "Overdue":
                display_tasks = overdue

            if dash_sort == "Priority":
                display_tasks = sorted(display_tasks, key=lambda t: -t.priority)
            elif dash_sort == "Date":
                display_tasks = sorted(display_tasks, key=lambda t: t.created_at)
            else:
                display_tasks = sorted(
                    display_tasks,
                    key=lambda t: (
                        scheduler.get_pet_by_id(t.pet_id).name
                        if scheduler.get_pet_by_id(t.pet_id)
                        else ""
                    ),
                )

            if display_tasks:
                cols = st.columns([1, 2, 3, 1, 1, 1])
                with cols[0]:
                    st.markdown("**Done**")
                with cols[1]:
                    st.markdown("**Pet**")
                with cols[2]:
                    st.markdown("**Task**")
                with cols[3]:
                    st.markdown("**Priority**")
                with cols[4]:
                    st.markdown("**Status**")
                with cols[5]:
                    st.markdown("**Freq**")

                for t in display_tasks:
                    pet = scheduler.get_pet_by_id(t.pet_id)
                    status = t.status.value.capitalize()
                    if t.is_overdue():
                        status = "⚠️ Overdue"
                    elif t.status == TaskStatus.COMPLETED:
                        status = "✅ Done"
                    elif t.status == TaskStatus.PENDING:
                        status = "⏳ Pending"

                    is_completed = t.status == TaskStatus.COMPLETED
                    priority_map = {1: "📘 Low", 2: "🟡 Med", 3: "🔴 High"}

                    cols = st.columns([1, 2, 3, 1, 1, 1])
                    with cols[0]:
                        checked = st.checkbox(
                            "",
                            value=is_completed,
                            key=f"dash_task_{t.id}",
                            label_visibility="hidden",
                        )
                        if checked and t.status != TaskStatus.COMPLETED:
                            scheduler.complete_task(t.id)
                            st.rerun()
                        elif not checked and t.status == TaskStatus.COMPLETED:
                            t.mark_pending()
                            st.rerun()
                    with cols[1]:
                        st.caption(f"🐾 {pet.name if pet else '?'}")
                    with cols[2]:
                        st.caption(
                            f"{t.title[:35]}{'...' if len(t.title) > 35 else ''}"
                        )
                    with cols[3]:
                        st.caption(priority_map.get(t.priority, ""))
                    with cols[4]:
                        st.caption(status)
                    with cols[5]:
                        st.caption(t.frequency.value.title())
            else:
                st.info(f"No {dash_filter.lower()} tasks")

    with tab3:
        all_tasks = owner.get_all_tasks()

        if not all_tasks:
            st.warning("⚠️ Add tasks first to generate a schedule!")
        else:
            s1, s2, s3 = st.columns([1, 1, 1])
            with s1:
                schedule_sort = st.selectbox(
                    "Sort by",
                    ["Priority", "Date", "Pet Name", "Status"],
                    key="sched_sort",
                )
            with s2:
                include_completed = st.checkbox("Include completed", value=False)
            with s3:
                st.write("")
                if st.button(
                    "🔄 Generate Schedule", use_container_width=True, type="primary"
                ):
                    schedule = scheduler.generate_schedule(owner_id="owner_1")
                    sort_map = {
                        "Priority": "priority",
                        "Date": "date",
                        "Pet Name": "pet_name",
                        "Status": "status",
                    }

                    scheduled_tasks = schedule.generate_schedule(
                        include_completed=include_completed,
                        sort_by=sort_map[schedule_sort],
                    )

                    if scheduled_tasks:
                        st.success(f"✅ **{len(scheduled_tasks)}** tasks scheduled")

                        cols = st.columns([1, 1, 3, 1, 1, 1, 1])
                        with cols[0]:
                            st.markdown("**#**")
                        with cols[1]:
                            st.markdown("**Done**")
                        with cols[2]:
                            st.markdown("**Task**")
                        with cols[3]:
                            st.markdown("**Pet**")
                        with cols[4]:
                            st.markdown("**P**")
                        with cols[5]:
                            st.markdown("**Status**")
                        with cols[6]:
                            st.markdown("**Freq**")

                        for i, t in enumerate(scheduled_tasks, 1):
                            pet = scheduler.get_pet_by_id(t.pet_id)
                            status = t.status.value.capitalize()
                            if t.is_overdue():
                                status = "⚠️"
                            elif t.status == TaskStatus.COMPLETED:
                                status = "✅"
                            elif t.status == TaskStatus.PENDING:
                                status = "⏳"

                            is_completed = t.status == TaskStatus.COMPLETED

                            cols = st.columns([1, 1, 3, 1, 1, 1, 1])
                            with cols[0]:
                                st.caption(f"**{i}**")
                            with cols[1]:
                                checked = st.checkbox(
                                    "",
                                    value=is_completed,
                                    key=f"sched_task_{t.id}",
                                    label_visibility="hidden",
                                )
                                if checked and t.status != TaskStatus.COMPLETED:
                                    scheduler.complete_task(t.id)
                                    st.rerun()
                                elif not checked and t.status == TaskStatus.COMPLETED:
                                    t.mark_pending()
                                    st.rerun()
                            with cols[2]:
                                st.caption(
                                    f"{t.title[:32]}{'...' if len(t.title) > 32 else ''}"
                                )
                            with cols[3]:
                                st.caption(pet.name if pet else "?")
                            with cols[4]:
                                st.caption({1: "📘", 2: "🟡", 3: "🔴"}[t.priority])
                            with cols[5]:
                                st.caption(status)
                            with cols[6]:
                                st.caption(t.frequency.value[:3].title())
                    else:
                        st.info("No tasks to schedule")

                    owner.add_schedule(schedule)

            st.divider()
            st.markdown("**📜 Schedule History**")
            if owner.schedules:
                for sched in owner.schedules[:5]:
                    with st.expander(
                        f"Schedule {sched.id} - {sched.date.strftime('%Y-%m-%d %H:%M')}"
                    ):
                        tc = len(sched.scheduled_tasks) if sched.scheduled_tasks else 0
                        st.info(
                            f"📅 {sched.date.strftime('%B %d, %Y')} | 📋 {tc} tasks"
                        )
            else:
                st.caption("No schedules yet")
else:
    st.info("👆 **Create an owner first using the form above!**")
