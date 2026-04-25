import os
import re
import sys
import importlib.util
import datetime
from typing import Optional
from google import genai
from dotenv import load_dotenv

load_dotenv()


def load_data_storage_module():
    spec = importlib.util.spec_from_file_location("data_storage", "data_storage.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


storage = load_data_storage_module().DataStorage()


NON_PET_KEYWORDS = [
    "human food",
    "people food",
    "adult entertainment",
    "weed",
    "cannabis",
    "marijuana",
    "cigarette",
    "tobacco",
    "alcohol",
    "beer",
    "wine",
    "liquor",
    "gun",
    "weapon",
    "firearm",
    "ammunition",
    "adult toy",
    "成人",
    "情趣",
]

PROMPT_INJECTION_PATTERNS = [
    r"\bignore\s+(all\s+)?(previous\s+)?(instructions?\s+)?(and\s+)?",
    r"\bignore\s+all\s+rules?\b",
    r"\byou\s+are\s+now\b",
    r"\b pretending?\b.*\bhelpful\b",
    r"\bpretend\s+(you\s+)?(is|are)\b",
    r"\bDAN\b.*\bdo\s+anything\b",
    r"\bdeveloper\s+mode\b",
    r"\bsudo\b.*\badmin\b",
    r"-->",
    r"<--",
    r"'{1}.*DROP\s+TABLE",
    r"DROP\s+TABLE",
    r"DROP\s+DATABASE",
    r"DELETE\s+FROM",
    r"INSERT\s+INTO",
    r"<script[^>]*>.*</script>",
    r"javascript:",
    r"onerror\s*=",
    r"onclick\s*=",
    r";\s*rm\s+-rf",
    r";\s*del\s+/[sq]",
    r";\s*format\s+[c-z]:",
    r"BASE64",
    r"eval\s*\(",
    r"exec\s*\(",
    r"\[IGNORE\]",
    r"\[/IGNORE\]",
    r"{{IGNORE}}",
    r"{{/IGNORE}}",
    r"\\x00",
    r"\\x[0-9a-fA-F]{2}",
]

PROMPT_INJECTION_KEYWORDS = [
    "hack",
    "illegal",
    "bomb",
    "explosive",
    "kill",
    "murder",
    "steal",
    "fraud",
    "scam",
    "phishing",
    "malware",
    "virus",
    "spyware",
    "ransomware",
    "ddos",
    "breach",
    "leak data",
    "secret api",
    "password",
    "credential",
    "bypass",
    "crack",
    "root access",
    "admin access",
]


def detect_prompt_injection(query: str) -> tuple[bool, Optional[str]]:
    query_lower = query.lower()

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, query_lower, re.IGNORECASE):
            return (
                False,
                "I cannot process requests that appear to contain instructions designed to bypass my guidelines.",
            )

    for keyword in PROMPT_INJECTION_KEYWORDS:
        if keyword in query_lower:
            return (
                False,
                "I cannot help with requests that involve harmful or illegal activities.",
            )

    return True, None


def is_pet_task_query(query: str) -> tuple[bool, Optional[str]]:
    injection_valid, injection_error = detect_prompt_injection(query)
    if not injection_valid:
        return False, injection_error

    query_lower = query.lower()

    for keyword in NON_PET_KEYWORDS:
        if keyword in query_lower:
            return (
                False,
                "This request is outside the scope of pet care I can help with.",
            )

    pet_task_keywords = [
        "pet",
        "pets",
        "dog",
        "dogs",
        "cat",
        "cats",
        "animal",
        "task",
        "tasks",
        "walk",
        "feeding",
        "feed",
        "grooming",
        "vet",
        "veterinarian",
        "health",
        "care",
        "training",
        "exercise",
        "breed",
        "weight",
        "age",
        "schedule",
        "pending",
        "completed",
        "overdue",
        "due",
        "today",
        "tomorrow",
        "soon",
    ]

    keyword_found = any(keyword in query_lower for keyword in pet_task_keywords)
    if not keyword_found:
        return (
            False,
            "I can only help with questions about your pets and their tasks. Please ask about your registered pets, their tasks, schedules, or pet care.",
        )

    return True, None


def format_pawpal_data_summary(owners) -> str:
    if not owners:
        return "No pet owners registered in the system."

    lines = ["[OWNERS]", ""]

    for owner in owners:
        owner_name = owner.name
        owner_email = owner.email
        lines.append(f"@{owner_name} ({owner_email}):")

        pets = owner.pets
        if not pets:
            lines.append("  -no pets-")
            continue

        for pet in pets:
            pet_name = pet.name
            animal = pet.animal
            age = pet.age
            lines.append(f"  {pet_name} [{animal}] age={age}:")

            tasks = pet.tasks
            if not tasks:
                lines.append("    no tasks")
                continue

            for task in tasks:
                task_title = task.title
                task_priority = task.priority
                task_status = (
                    task.status.value if hasattr(task.status, "value") else task.status
                )
                task_date = task.assigned_date
                date_str = ""
                if task_date:
                    try:
                        dt = (
                            task_date
                            if isinstance(task_date, datetime)
                            else datetime.fromisoformat(str(task_date))
                        )
                        date_str = f" due={dt.strftime('%m/%d %H:%M')}"
                    except:
                        pass
                lines.append(
                    f"    [{task_status}] {task_title} (p{task_priority}){date_str}"
                )

        lines.append("")

    return "\n".join(lines)


def init_gemini():
    client = genai.Client()
    return client


def chatbot_query(user_query: str) -> str:
    is_valid, error_message = is_pet_task_query(user_query)

    if not is_valid:
        return error_message

    try:
        client = init_gemini()
        owners = storage.load_all()
        data_summary = format_pawpal_data_summary(owners)

        prompt = f"""You are a pet care assistant for PawPal. Use ONLY the data below to answer the user's question.

Your Guidelines:
1. Only answer questions about the pets and tasks listed in the provided data
2. If the user asks about a pet or task not in the data, state that it's not registered
3. Provide helpful, concise information about the pet's care tasks, schedule, and status
4. For task-related questions, include priority and status (pending/completed/overdue)
5. Be friendly and helpful

=== DATA START ===
{data_summary}
=== DATA END ===

User Question: {user_query}

Provide a helpful response based ONLY on the data above. If the question cannot be answered from this data, explain that you can only help with registered pets and tasks."""

        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
        )

        result = response.text

        if any(keyword in result.lower() for keyword in NON_PET_KEYWORDS):
            return "I can only provide information about your registered pets and their tasks. Please ask about your pets or their care tasks."

        return result

    except Exception as e:
        return f"I encountered an error: {str(e)}. Please try again or check if GOOGLE_API_KEY is configured."


def chatbot_with_guardrails(user_query: str) -> str:
    is_valid, error_message = is_pet_task_query(user_query)

    if not is_valid:
        return error_message

    result = chatbot_query(user_query)

    if any(keyword in result.lower() for keyword in NON_PET_KEYWORDS):
        return "I can only provide information about your registered pets and their tasks. Please ask about your pets or their care tasks."

    return result
