# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Features

- **Owner Management**: Create and manage pet owner profiles with name and email
- **Pet Management**: Add multiple pets with species, breed, age, and weight tracking
- **Task Management**: Create care tasks with title, description, priority (Low/Medium/High), and frequency (Daily/Weekly/Monthly/One-time)
- **Task Status Tracking**: Automatic tracking of pending, completed, overdue, and cancelled tasks
- **Smart Scheduling**: Generate daily schedules sorted by priority, date, pet name, or status
- **Recurring Tasks**: Automatic rescheduling of daily and weekly tasks upon completion
- **Conflict Detection**: Identifies when multiple tasks are scheduled at the same time
- **Dashboard View**: KPI metrics showing total, pending, completed, and overdue tasks
- **Multi-Pet Support**: Manage tasks across multiple pets under one owner
- **System Statistics**: Real-time stats on owners, pets, and tasks across the system
- **Task Filtering & Sorting**: Filter by status and sort by priority, date, or pet name

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup
Frontend
```bash
cd frontend
pnpm install
pnpm run dev
```

Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python api.py
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+
```bash
python3 -m pytest
```

My tests cover multiple things:
1. checks if a task has been checked off and completed
2. checks if the number of tasks has increased for a pet if we add a task for them
3. checks if tasks are sorted correctly by various factors like date, priority, and pet
4. checks if recurring tasks are handled correctly
5. checks for edge cases and sees of they are accounted for like schedule/task conflicts and empty dates assigned

My confidence level on the system's reliability lies around a 4-4.5 stars based on the tests

## 📸 Demo
<a href="/course_images/pawpal-ui.png" target="_blank"><img src='/course_images/pawpal-ui.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>.
