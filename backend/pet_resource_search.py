import os
import re
import json
from typing import Optional
from google import genai
from dotenv import load_dotenv

load_dotenv()

DATA_FILE = "pawpal_data.json"

ALLOWED_PET_CATEGORIES = [
    "pet food",
    "pet foods",
    "dog food",
    "cat food",
    "bird food",
    "rabbit food",
    "pet treats",
    "dog treats",
    "cat treats",
    "pet toys",
    "pet toy",
    "dog toys",
    "cat toys",
    "bird toys",
    "pet supplies",
    "pet supply",
    "pet accessories",
    "pet shelter",
    "pet shelters",
    "animal shelter",
    "animal shelters",
    "pet store",
    "pet stores",
    "veterinarian",
    "veterinarians",
    "vet",
    "vets",
    "veterinary",
    "pet grooming",
    "pet groomer",
    "grooming",
    "pet insurance",
    "pet medical",
    "pet training",
    "pet trainer",
    "dog trainer",
    "cat trainer",
    "pet daycare",
    "pet sitting",
    "dog walking",
    "pet rescue",
    "pet rescue organization",
    "adopt pet",
    "adopt a pet",
    "pet adoption",
    "pet food brand",
    "pet food brands",
    "organic pet food",
    "grain free pet food",
    "pet bed",
    "pet beds",
    "pet crate",
    "pet carrier",
    "pet collar",
    "pet leash",
    "pet harness",
    "pet medication",
    "pet meds",
    "flea treatment",
    "heartworm prevention",
    "pet vitamin",
    "pet supplements",
    "aquarium",
    "fish tank",
    "pet fish",
    "pet cage",
    "bird cage",
    "hamster cage",
]

ALLOWED_RETAILERS = [
    "chewy",
    "chewy.com",
    "petco",
    "petco.com",
    "petsmart",
    "petsmart.com",
    "pet smart",
    "amazon",
    "amazon.com",
    "walmart",
    "walmart.com",
    "target",
    "target.com",
    "pet supplies plus",
    "petsuppliesplus.com",
    "bed bath & beyond",
    "bedbathandbeyond.com",
    "costco",
    "costco.com",
    "nordstrom",
    "nordstrom.com",
    "pet store",
    "local pet store",
]

RESOURCE_PATTERNS = [
    r"chewy\.com",
    r"petco\.com",
    r"petsmart\.com",
    r"amazon\.com",
    r"walmart\.com",
    r"target\.com",
    r"petsuppliesplus\.com",
    r"costco\.com",
]

COMMERCIAL_KEYWORDS = [
    "pet food",
    "pet treats",
    "pet toys",
    "pet supplies",
    "pet accessories",
    "pet bed",
    "pet crate",
    "pet carrier",
    "pet collar",
    "pet leash",
    "pet harness",
    "pet medication",
    "pet vitamin",
    "pet supplements",
    "flea treatment",
    "heartworm",
    "pet insurance",
    "adopt",
    "shelter",
    "rescue",
    "veterinarian",
    "vet",
    "grooming",
    "training",
    "daycare",
    "sitting",
    "walking",
    "food",
    "treats",
    "toys",
    "supplies",
    "bed",
    "crate",
    "carrier",
    "collar",
    "leash",
    "harness",
    "medication",
    "vitamin",
    "supplements",
    "insurance",
]

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
    r"BASE64",
    r"eval\s*\(",
    r"exec\s*\(",
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


def load_owners_from_data(filepath: str = DATA_FILE) -> list[dict]:
    """Load owner data from pawpal_data.json."""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            return data.get("owners", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def get_first_owner_with_pets(filepath: str = DATA_FILE) -> Optional[dict]:
    """Get the first owner with registered pets."""
    owners = load_owners_from_data(filepath)
    for owner in owners:
        if owner.get("pets") and len(owner.get("pets", [])) > 0:
            return owner
    return None


def get_owner_pets(owner: dict) -> list[dict]:
    """Extract pets from owner dict."""
    return owner.get("pets", [])


def get_owner_preferences(owner: dict) -> dict:
    """Extract preferences from owner dict."""
    return owner.get("preferences", {})


def detect_prompt_injection(query: str) -> tuple[bool, Optional[str]]:
    """Check for prompt injection attempts."""
    query_lower = query.lower()

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, query_lower, re.IGNORECASE):
            return False, "I cannot process that request."

    for keyword in PROMPT_INJECTION_KEYWORDS:
        if keyword in query_lower:
            return False, "I cannot help with that."

    return True, None


def init_gemini():
    """Initialize Gemini client."""
    client = genai.Client()
    return client


def is_pet_related_query(query: str) -> tuple[bool, Optional[str]]:
    """Check if query is pet-related with light guardrails."""
    injection_valid, injection_error = detect_prompt_injection(query)
    if not injection_valid:
        return False, injection_error

    query_lower = query.lower()

    for keyword in NON_PET_KEYWORDS:
        if keyword in query_lower:
            return False, "That request is outside my pet-related scope."

    for category in ALLOWED_PET_CATEGORIES:
        if category in query_lower:
            return True, None

    return True, None


def contains_allowed_retailer(text: str) -> bool:
    """Check if text contains allowed retailers."""
    text_lower = text.lower()
    for retailer in ALLOWED_RETAILERS:
        if retailer in text_lower:
            return True
    return False


def format_pet_context(pets: list[dict]) -> str:
    """Format pet information for prompts."""
    if not pets:
        return "No pets registered."

    lines = []
    for pet in pets:
        name = pet.get("name", "Unknown")
        animal = pet.get("animal", "pet")
        breed = pet.get("breed", "Unknown")
        age = pet.get("age", "Unknown")
        weight = pet.get("weight", "Unknown")
        lines.append(f"- {name} ({animal}): {breed}, {age} years old, {weight} lbs")

    return "\n".join(lines)


def search_pet_resources(
    query: str,
    owner_data: Optional[dict] = None,
    include_pet_context: bool = True,
) -> str:
    """Search for pet resources, optionally using owner/pet info."""
    is_valid, error_message = is_pet_related_query(query)
    if not is_valid:
        return error_message

    try:
        client = init_gemini()
    except ValueError as e:
        return f"Error: {str(e)}. Please set GOOGLE_API_KEY."

    pet_context = ""
    preferences = {}

    if owner_data and include_pet_context:
        pets = get_owner_pets(owner_data)
        preferences = get_owner_preferences(owner_data)

        if pets:
            pet_context = f"""
Owner Context:
The owner has the following pets:
{format_pet_context(pets)}
"""
            budget = preferences.get("budget", "")
            if budget:
                pet_context += f"Budget: {budget}\n"

            preferred = preferences.get("preferred_retailers", [])
            if preferred:
                pet_context += f"Preferred retailers: {', '.join(preferred)}\n"

    prompt = f"""You are a pet resource assistant. Search for pet-related resources, products, and services based on: "{query}"
{pet_context}
Focus on:
- Best prices, deals, discounts, and cheap options across retailers
- Stock availability (in stock, low stock, out of stock)
- Compare prices between Chewy, Petco, PetSmart, Amazon, Walmart, Target

For each result provide:
1. Product name and retailer
2. Price (current, sale price, price comparison)
3. Stock status (in stock/out of stock)
4. Brief description

Only provide results from trusted pet retailers. Recommend consulting a veterinarian for dietary advice."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
        )

        results_text = response.text

        if not contains_allowed_retailer(results_text):
            return f"I found info but couldn't verify retailer sources. Try checking Chewy, Petco, or PetSmart directly."

        return results_text

    except Exception as e:
        return f"Error searching: {str(e)}. Please check GOOGLE_API_KEY."


def search_pet_resources_with_owner(
    query: str,
    filepath: str = DATA_FILE,
) -> str:
    """Search for pet resources using owner data from pawpal_data.json."""
    owner = get_first_owner_with_pets(filepath)

    if owner:
        return search_pet_resources(query, owner_data=owner)
    else:
        return search_pet_resources(query, owner_data=None)


def search_pet_resources_simple(query: str) -> str:
    """Simple search without owner context."""
    return search_pet_resources(query, owner_data=None, include_pet_context=False)
